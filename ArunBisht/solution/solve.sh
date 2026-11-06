#!/bin/bash
set -euo pipefail

cd /workspace/repo

cat > go.mod << 'EOF'
module titlecasego

go 1.23
EOF

cat > main.go << 'EOF'
package main

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"strings"
	"unicode"
)

// Punctuation matched by the Python character class after regex escapes.
const punct = "!\"#$%&'()*+,-./:;?@[\\]_`{|}~\u2012\u2013\u2014\u2015\u2018\u201c"

// Marks that start a sub-phrase when followed by a space: : . ; ? ! - – ‒ — ―
const subMarks = ":.;?!-\u2012\u2013\u2014\u2015"

type alt struct {
	lit    string
	optDot bool
}

// Order matches the Python alternation. The first branch that fits wins.
var smallAlts = []alt{
	{"a", false},
	{"an", false},
	{"and", false},
	{"as", false},
	{"at", false},
	{"but", false},
	{"by", false},
	{"en", false},
	{"for", false},
	{"if", false},
	{"in", false},
	{"of", false},
	{"on", false},
	{"or", false},
	{"the", false},
	{"to", false},
	{"v", true},
	{"via", false},
	{"vs", true},
}

func main() {
	in, err := io.ReadAll(os.Stdin)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	text := string(in)
	lines := strings.Split(text, "\n")
	if len(lines) > 0 && lines[len(lines)-1] == "" {
		lines = lines[:len(lines)-1]
	}
	out := bufio.NewWriter(os.Stdout)
	for _, line := range lines {
		line = strings.TrimSuffix(line, "\r")
		fmt.Fprintln(out, titlecase(line, true))
	}
	if err := out.Flush(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func titlecase(text string, smallFirstLast bool) string {
	if strings.ContainsAny(text, "\r\n") {
		parts := collapseNewlines(text)
		out := make([]string, len(parts))
		for i, part := range parts {
			out[i] = titlecaseLine(part, smallFirstLast)
		}
		return strings.Join(out, "\n")
	}
	return titlecaseLine(text, smallFirstLast)
}

func collapseNewlines(text string) []string {
	var lines []string
	start := 0
	for i := 0; i < len(text); i++ {
		if text[i] != '\n' && text[i] != '\r' {
			continue
		}
		lines = append(lines, text[start:i])
		if text[i] == '\r' && i+1 < len(text) && text[i+1] == '\n' {
			i++
		}
		start = i + 1
	}
	lines = append(lines, text[start:])
	var out []string
	for _, line := range lines {
		if line == "" {
			continue
		}
		out = append(out, line)
	}
	if len(out) == 0 {
		return []string{""}
	}
	if strings.HasSuffix(text, "\n") || strings.HasSuffix(text, "\r") {
		out = append(out, "")
	}
	return out
}

func titlecaseLine(line string, smallFirstLast bool) string {
	allCaps := line == strings.ToUpper(line)
	words, spaces := splitSpaces(line)
	tc := make([]string, len(words))
	for i, word := range words {
		tc[i] = titleWord(word, allCaps)
	}
	if smallFirstLast && len(tc) > 0 {
		tc[0] = applySmallFirst(tc[0])
		tc[len(tc)-1] = applySmallLast(tc[len(tc)-1])
	}
	return applySubphrase(joinWords(tc, spaces))
}

func titleWord(word string, allCaps bool) string {
	r := []rune(word)
	if allCaps && isInitials(r) {
		return word
	}
	if isApos(r) {
		return fixApos(r)
	}
	if pre, rest, ok := splitMc(r); ok {
		return string(pre) + titlecase(string(rest), true)
	}
	if isHonorific(word) {
		return upperFirst(word) + restOf(word)
	}
	if hasInlinePeriod(r) || (!allCaps && hasUpperElsewhere(r)) {
		return word
	}
	if fullSmall(r) {
		return strings.ToLower(word)
	}
	if strings.Contains(word, "/") && !strings.Contains(word, "//") {
		parts := strings.Split(word, "/")
		for i, part := range parts {
			parts[i] = titlecase(part, false)
		}
		return strings.Join(parts, "/")
	}
	if strings.Contains(word, "-") {
		parts := strings.Split(word, "-")
		for i, part := range parts {
			parts[i] = titlecase(part, false)
		}
		return strings.Join(parts, "-")
	}
	if allCaps {
		word = strings.ToLower(word)
		r = []rune(word)
	}
	if len(r) > 2 && allConsonants(r) {
		return strings.ToUpper(word)
	}
	return capFirst(r)
}

func splitSpaces(line string) (words, spaces []string) {
	var b strings.Builder
	flush := func() {
		words = append(words, b.String())
		b.Reset()
	}
	for _, r := range line {
		if isSpace(r) {
			flush()
			spaces = append(spaces, string(r))
		} else {
			b.WriteRune(r)
		}
	}
	flush()
	return words, spaces
}

func joinWords(words, spaces []string) string {
	var b strings.Builder
	for i, word := range words {
		b.WriteString(word)
		if i < len(spaces) {
			b.WriteString(spaces[i])
		}
	}
	return b.String()
}

func isSpace(r rune) bool {
	switch r {
	case '\t', '\n', '\v', '\f', '\r', '\u0085', '\u00a0':
		return true
	}
	return unicode.Is(unicode.Zs, r)
}

func isPunct(r rune) bool {
	return strings.ContainsRune(punct, r)
}

func isWord(r rune) bool {
	return r == '_' || unicode.IsLetter(r) || unicode.IsDigit(r)
}

func isBoundary(r []rune, i int) bool {
	left := i > 0 && isWord(r[i-1])
	right := i < len(r) && isWord(r[i])
	return left != right
}

func hasPrefixFold(r []rune, lit string) bool {
	l := []rune(lit)
	if len(r) < len(l) {
		return false
	}
	return strings.EqualFold(string(r[:len(l)]), lit)
}

func matchSmall(r []rune, i int, cond func(end int) bool) (int, bool) {
	for _, a := range smallAlts {
		if !hasPrefixFold(r[i:], a.lit) {
			continue
		}
		base := i + len([]rune(a.lit))
		if a.optDot && base < len(r) && r[base] == '.' {
			if cond(base + 1) {
				return base + 1, true
			}
		}
		if cond(base) {
			return base, true
		}
	}
	return 0, false
}

func fullSmall(r []rune) bool {
	_, ok := matchSmall(r, 0, func(end int) bool { return end == len(r) })
	return ok
}

func applySmallFirst(s string) string {
	r := []rune(s)
	for k := 0; k <= len(r); k++ {
		if k > 0 && !isPunct(r[k-1]) {
			break
		}
		end, ok := matchSmall(r, k, func(end int) bool { return isBoundary(r, end) })
		if !ok {
			continue
		}
		return string(r[:k]) + pyCapitalize(string(r[k:end])) + string(r[end:])
	}
	return s
}

func applySmallLast(s string) string {
	r := []rune(s)
	for start := 0; start <= len(r); start++ {
		if !isBoundary(r, start) {
			continue
		}
		end, ok := matchSmall(r, start, func(end int) bool {
			if end == len(r) {
				return true
			}
			return end+1 == len(r) && isPunct(r[end])
		})
		if !ok {
			continue
		}
		matchEnd := end
		if end < len(r) {
			matchEnd = len(r)
		}
		return string(r[:start]) + pyCapitalize(string(r[start:matchEnd]))
	}
	return s
}

func applySubphrase(s string) string {
	r := []rune(s)
	var b strings.Builder
	for i := 0; i < len(r); {
		if i+1 < len(r) && strings.ContainsRune(subMarks, r[i]) && r[i+1] == ' ' {
			if end, ok := matchSmall(r, i+2, func(int) bool { return true }); ok {
				b.WriteRune(r[i])
				b.WriteRune(' ')
				b.WriteString(pyCapitalize(string(r[i+2 : end])))
				i = end
				continue
			}
		}
		b.WriteRune(r[i])
		i++
	}
	return b.String()
}

func isInitials(r []rune) bool {
	var walk func(i int, consumed bool) bool
	walk = func(i int, consumed bool) bool {
		if i == len(r) {
			return consumed
		}
		if i+1 < len(r) && unicode.IsUpper(r[i]) && r[i+1] == '.' {
			if walk(i+2, true) {
				return true
			}
		}
		if i+2 < len(r) && unicode.IsUpper(r[i]) && r[i+1] == '.' && unicode.IsUpper(r[i+2]) {
			if walk(i+3, true) {
				return true
			}
		}
		return false
	}
	return walk(0, false)
}

func isApos(r []rune) bool {
	if len(r) < 3 {
		return false
	}
	switch unicode.ToLower(r[0]) {
	case 'd', 'o', 'l':
	default:
		return false
	}
	if r[1] != '\'' && r[1] != '\u2018' {
		return false
	}
	i := 2
	if !unicode.IsLetter(r[i]) {
		return false
	}
	for i < len(r) && unicode.IsLetter(r[i]) {
		i++
	}
	if i == len(r) {
		return true
	}
	if len(r)-i != 2 {
		return false
	}
	for _, c := range r[i:] {
		cl := unicode.ToLower(c)
		if cl != '\'' && cl != 's' {
			return false
		}
	}
	return true
}

func fixApos(r []rune) string {
	first := string(r[0])
	if !strings.ContainsRune("aeiouAEIOU", r[0]) {
		first = strings.ToLower(first)
	} else {
		first = strings.ToUpper(first)
	}
	return first + string(r[1]) + strings.ToUpper(string(r[2])) + string(r[3:])
}

func splitMc(r []rune) (pre, rest []rune, ok bool) {
	if len(r) < 4 {
		return nil, nil, false
	}
	mc := (r[0] == 'M' || r[0] == 'm') && r[1] == 'c'
	upper := r[0] == 'M' && r[1] == 'C'
	if !mc && !upper {
		return nil, nil, false
	}
	rest = r[2:]
	if len(rest) < 2 || !isWord(rest[0]) {
		return nil, nil, false
	}
	return []rune{'M', 'c'}, rest, true
}

func isHonorific(word string) bool {
	switch strings.ToLower(word) {
	case "mr", "mrs", "ms", "dr":
		return true
	default:
		return false
	}
}

func upperFirst(word string) string {
	r := []rune(word)
	if len(r) == 0 {
		return ""
	}
	return strings.ToUpper(string(r[0]))
}

func restOf(word string) string {
	r := []rune(word)
	if len(r) < 2 {
		return ""
	}
	return string(r[1:])
}

func hasInlinePeriod(r []rune) bool {
	for i := 0; i+2 < len(r); i++ {
		if unicode.IsLetter(r[i]) && r[i+1] == '.' && unicode.IsLetter(r[i+2]) {
			return true
		}
	}
	return false
}

func hasUpperElsewhere(r []rune) bool {
	i := 0
	for i < len(r) && isPunct(r[i]) {
		i++
	}
	if i >= len(r) || !unicode.IsLetter(r[i]) {
		return false
	}
	for j := i + 1; j < len(r); j++ {
		if !unicode.IsLetter(r[j]) {
			return false
		}
		if unicode.IsUpper(r[j]) {
			return true
		}
	}
	return false
}

func allConsonants(r []rune) bool {
	if len(r) == 0 {
		return false
	}
	for _, c := range r {
		cl := unicode.ToLower(c)
		if cl < 'a' || cl > 'z' || strings.ContainsRune("aeiouy", cl) {
			return false
		}
	}
	return true
}

func capFirst(r []rune) string {
	i := 0
	for i < len(r) && isPunct(r[i]) {
		i++
	}
	if i >= len(r) || !unicode.IsLetter(r[i]) {
		return string(r)
	}
	return strings.ToUpper(string(r[:i+1])) + string(r[i+1:])
}

func pyCapitalize(s string) string {
	r := []rune(s)
	if len(r) == 0 {
		return ""
	}
	return strings.ToUpper(string(r[0])) + strings.ToLower(string(r[1:]))
}
EOF

find /workspace/repo -type f -name '*.py' -delete
rm -rf /workspace/repo/titlecase
find /workspace/repo -type d -empty -delete
