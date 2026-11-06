#!/bin/bash
set -euo pipefail
cd /workspace/repo

cat > go.mod << 'EOF'
module titlecase

go 1.23
EOF

cat > main.go << 'ENDGO'
package main

import (
	"bufio"
	"io"
	"os"
	"strings"
	"unicode"
)

// titlecase ports python-titlecase 2.4.1 in its standard-library re mode
// (the optional third-party regex package is not installed). Each call uses
// the same default arguments as titlecase(): no callback, blank-line runs
// collapsed, original whitespace kept. smallFirstLast is false only when the
// Python function recurses through slash or hyphen parts.

func main() {
	in := bufio.NewReader(os.Stdin)
	for {
		line, err := in.ReadString('\n')
		if len(line) > 0 {
			line = strings.TrimSuffix(line, "\n")
			line = strings.TrimSuffix(line, "\r")
			os.Stdout.WriteString(titlecase(line, true))
			os.Stdout.WriteString("\n")
		}
		if err == io.EOF {
			break
		}
		if err != nil {
			os.Stderr.WriteString(err.Error() + "\n")
			os.Exit(1)
		}
	}
}

func titlecase(text string, smallFirstLast bool) string {
	lines := splitNewlines(text)
	out := make([]string, len(lines))
	for i, line := range lines {
		out[i] = titlecaseLine(line, smallFirstLast)
	}
	return strings.Join(out, "\n")
}

func splitNewlines(text string) []string {
	var lines []string
	start := 0
	for i := 0; i < len(text); i++ {
		if text[i] == '\n' || text[i] == '\r' {
			lines = append(lines, text[start:i])
			for i+1 < len(text) && (text[i+1] == '\n' || text[i+1] == '\r') {
				i++
			}
			start = i + 1
		}
	}
	lines = append(lines, text[start:])
	return lines
}

func titlecaseLine(line string, smallFirstLast bool) string {
	allCaps := strings.ToUpper(line) == line
	words, spaces := splitSpaces(line)
	tc := make([]string, len(words))
	for i, word := range words {
		tc[i] = titlecaseWord(word, allCaps)
	}
	if smallFirstLast && len(tc) > 0 {
		tc[0] = applySmallFirst(tc[0])
		tc[len(tc)-1] = applySmallLast(tc[len(tc)-1])
	}
	return applySubphrase(joinPieces(tc, spaces))
}

func titlecaseWord(word string, allCaps bool) string {
	rs := []rune(word)
	if allCaps && matchInitials(rs) {
		return word
	}
	if matchApos(rs) {
		return applyApos(word)
	}
	if prefix, rest, ok := splitMc(word); ok {
		return pyCapitalize(prefix) + titlecase(rest, true)
	}
	if matchMr(word) {
		r := []rune(word)
		return strings.ToUpper(string(r[0])) + string(r[1:])
	}
	if hasInlinePeriod(rs) || (!allCaps && hasUCElsewhere(rs)) {
		return word
	}
	if isExactSmall(rs) {
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
		rs = []rune(word)
	}
	if len(rs) > 2 && isAllConsonants(rs) {
		return strings.ToUpper(word)
	}
	return capFirst(word)
}

func splitSpaces(line string) (words, spaces []string) {
	var cur strings.Builder
	for _, r := range line {
		if isPySpace(r) {
			words = append(words, cur.String())
			cur.Reset()
			spaces = append(spaces, string(r))
			continue
		}
		cur.WriteRune(r)
	}
	words = append(words, cur.String())
	return words, spaces
}

func joinPieces(words, spaces []string) string {
	var b strings.Builder
	for i, word := range words {
		if i > 0 {
			b.WriteString(spaces[i-1])
		}
		b.WriteString(word)
	}
	return b.String()
}

func isPySpace(r rune) bool {
	switch r {
	case '\t', '\n', '\v', '\f', '\r', 0x1c, 0x1d, 0x1e, 0x1f:
		return true
	}
	return unicode.IsSpace(r)
}

func isWordRune(r rune) bool {
	if unicode.IsLetter(r) || unicode.IsNumber(r) {
		return true
	}
	if !unicode.Is(unicode.Pc, r) {
		return false
	}
	switch r {
	case 0x203F, 0x2040, 0x2054, 0xFE33, 0xFE34, 0xFE4D, 0xFE4E, 0xFE4F, 0xFF3F:
		return false
	}
	return true
}

func isPunct(r rune) bool {
	switch r {
	case '!', '"', '#', '$', '%', '&', '\'', '(', ')', '*', '+', ',', '-', '.', '/',
		':', ';', '?', '@', '[', '\\', ']', '_', '`', '{', '|', '}', '~',
		'\u2012', '\u2013', '\u2014', '\u2015', '\u2018', '\u201c':
		return true
	}
	return false
}

func isSubphrasePunct(r rune) bool {
	switch r {
	case ':', '.', ';', '?', '!', '-', '\u2012', '\u2013', '\u2014', '\u2015':
		return true
	}
	return false
}

func boundaryAt(rs []rune, i int) bool {
	left := i > 0 && isWordRune(rs[i-1])
	right := i < len(rs) && isWordRune(rs[i])
	return left != right
}

func pyCapitalize(s string) string {
	rs := []rune(s)
	if len(rs) == 0 {
		return ""
	}
	return strings.ToUpper(string(rs[0])) + strings.ToLower(string(rs[1:]))
}

type smallAlt int

const (
	altLit smallAlt = iota
	altV
	altVs
)

type alt struct {
	kind smallAlt
	text string
}

// Order matches the Python alternation, including v\.? before via.
var smallAlts = []alt{
	{altLit, "a"},
	{altLit, "an"},
	{altLit, "and"},
	{altLit, "as"},
	{altLit, "at"},
	{altLit, "but"},
	{altLit, "by"},
	{altLit, "en"},
	{altLit, "for"},
	{altLit, "if"},
	{altLit, "in"},
	{altLit, "of"},
	{altLit, "on"},
	{altLit, "or"},
	{altLit, "the"},
	{altLit, "to"},
	{altV, ""},
	{altLit, "via"},
	{altVs, ""},
}

func foldEq(rs []rune, word string) bool {
	wr := []rune(word)
	if len(rs) != len(wr) {
		return false
	}
	for i := range wr {
		if unicode.ToLower(rs[i]) != unicode.ToLower(wr[i]) {
			return false
		}
	}
	return true
}

func isExactSmall(rs []rune) bool {
	for _, a := range smallAlts {
		if matchAltExact(a, rs) {
			return true
		}
	}
	return false
}

func matchAltExact(a alt, rs []rune) bool {
	switch a.kind {
	case altLit:
		return foldEq(rs, a.text)
	case altV:
		return foldEq(rs, "v") || foldEq(rs, "v.")
	case altVs:
		return foldEq(rs, "vs") || foldEq(rs, "vs.")
	}
	return false
}

func applySmallFirst(word string) string {
	rs := []rune(word)
	maxP := 0
	for maxP < len(rs) && isPunct(rs[maxP]) {
		maxP++
	}
	for p := maxP; p >= 0; p-- {
		end, ok := matchSmallBounded(rs, p)
		if !ok {
			continue
		}
		return string(rs[:p]) + pyCapitalize(string(rs[p:end])) + string(rs[end:])
	}
	return word
}

func matchSmallBounded(rs []rune, i int) (int, bool) {
	for _, a := range smallAlts {
		end, ok := matchAltBounded(a, rs, i)
		if ok {
			return end, true
		}
	}
	return 0, false
}

func matchAltBounded(a alt, rs []rune, i int) (int, bool) {
	switch a.kind {
	case altLit:
		wr := []rune(a.text)
		end := i + len(wr)
		if end > len(rs) || !foldEq(rs[i:end], a.text) {
			return 0, false
		}
		if boundaryAt(rs, end) {
			return end, true
		}
		return 0, false
	case altV:
		return matchOptDotBounded(rs, i, 'v')
	case altVs:
		end := i + 2
		if end > len(rs) || !foldEq(rs[i:end], "vs") {
			return 0, false
		}
		if end < len(rs) && rs[end] == '.' && boundaryAt(rs, end+1) {
			return end + 1, true
		}
		if boundaryAt(rs, end) {
			return end, true
		}
		return 0, false
	}
	return 0, false
}

func matchOptDotBounded(rs []rune, i int, letter rune) (int, bool) {
	if i >= len(rs) || unicode.ToLower(rs[i]) != letter {
		return 0, false
	}
	if i+1 < len(rs) && rs[i+1] == '.' && boundaryAt(rs, i+2) {
		return i + 2, true
	}
	if boundaryAt(rs, i+1) {
		return i + 1, true
	}
	return 0, false
}

func applySmallLast(word string) string {
	rs := []rune(word)
	for i := 0; i <= len(rs); i++ {
		if !boundaryAt(rs, i) {
			continue
		}
		if matchSmallToEnd(rs, i) {
			return string(rs[:i]) + pyCapitalize(string(rs[i:]))
		}
	}
	return word
}

func matchSmallToEnd(rs []rune, i int) bool {
	for _, a := range smallAlts {
		if matchAltToEnd(a, rs, i) {
			return true
		}
	}
	return false
}

func matchAltToEnd(a alt, rs []rune, i int) bool {
	switch a.kind {
	case altLit:
		wr := []rune(a.text)
		n := len(wr)
		rest := len(rs) - i
		if rest == n && foldEq(rs[i:], a.text) {
			return true
		}
		if rest == n+1 && foldEq(rs[i:i+n], a.text) && isPunct(rs[i+n]) {
			return true
		}
		return false
	case altV:
		return optDotToEnd(rs, i, 'v')
	case altVs:
		if i+2 > len(rs) || !foldEq(rs[i:i+2], "vs") {
			return false
		}
		rest := rs[i+2:]
		switch len(rest) {
		case 0:
			return true
		case 1:
			return rest[0] == '.' || isPunct(rest[0])
		case 2:
			return rest[0] == '.' && isPunct(rest[1])
		default:
			return false
		}
	}
	return false
}

func optDotToEnd(rs []rune, i int, letter rune) bool {
	if i >= len(rs) || unicode.ToLower(rs[i]) != letter {
		return false
	}
	rest := rs[i+1:]
	switch len(rest) {
	case 0:
		return true
	case 1:
		return rest[0] == '.' || isPunct(rest[0])
	case 2:
		return rest[0] == '.' && isPunct(rest[1])
	default:
		return false
	}
}

func applySubphrase(s string) string {
	rs := []rune(s)
	var b strings.Builder
	for i := 0; i < len(rs); {
		end, ok := matchSubphraseAt(rs, i)
		if !ok {
			b.WriteRune(rs[i])
			i++
			continue
		}
		b.WriteRune(rs[i])
		b.WriteRune(rs[i+1])
		b.WriteString(pyCapitalize(string(rs[i+2 : end])))
		i = end
	}
	return b.String()
}

func matchSubphraseAt(rs []rune, i int) (int, bool) {
	if i+2 >= len(rs) || !isSubphrasePunct(rs[i]) || rs[i+1] != ' ' {
		return 0, false
	}
	return matchSmallPrefixCS(rs, i+2)
}

func matchSmallPrefixCS(rs []rune, i int) (int, bool) {
	for _, a := range smallAlts {
		end, ok := matchAltPrefixCS(a, rs, i)
		if ok {
			return end, true
		}
	}
	return 0, false
}

func matchAltPrefixCS(a alt, rs []rune, i int) (int, bool) {
	switch a.kind {
	case altLit:
		wr := []rune(a.text)
		end := i + len(wr)
		if end <= len(rs) && string(rs[i:end]) == a.text {
			return end, true
		}
		return 0, false
	case altV:
		if i < len(rs) && rs[i] == 'v' {
			if i+1 < len(rs) && rs[i+1] == '.' {
				return i + 2, true
			}
			return i + 1, true
		}
		return 0, false
	case altVs:
		if i+1 < len(rs) && rs[i] == 'v' && rs[i+1] == 's' {
			if i+2 < len(rs) && rs[i+2] == '.' {
				return i + 3, true
			}
			return i + 2, true
		}
		return 0, false
	}
	return 0, false
}

func hasInlinePeriod(rs []rune) bool {
	for i := 0; i+2 < len(rs); i++ {
		if isWordRune(rs[i]) && rs[i+1] == '.' && isWordRune(rs[i+2]) {
			return true
		}
	}
	return false
}

func hasUCElsewhere(rs []rune) bool {
	maxP := 0
	for maxP < len(rs) && isPunct(rs[maxP]) {
		maxP++
	}
	for p := 0; p <= maxP; p++ {
		if asciiUpperAfterLetter(rs[p:]) {
			return true
		}
	}
	return false
}

func asciiUpperAfterLetter(rs []rune) bool {
	for i := 0; i < len(rs) && isASCIILetter(rs[i]); i++ {
		if i >= 1 && rs[i] >= 'A' && rs[i] <= 'Z' {
			return true
		}
	}
	return false
}

func isASCIILetter(r rune) bool {
	return (r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z')
}

func capFirst(word string) string {
	rs := []rune(word)
	i := 0
	for i < len(rs) && isPunct(rs[i]) && !isWordRune(rs[i]) {
		i++
	}
	if i < len(rs) && isWordRune(rs[i]) {
		return strings.ToUpper(string(rs[:i+1])) + string(rs[i+1:])
	}
	return word
}

func isAllConsonants(rs []rune) bool {
	if len(rs) == 0 {
		return false
	}
	for _, r := range rs {
		switch unicode.ToLower(r) {
		case 'b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z':
		default:
			return false
		}
	}
	return true
}

func matchInitials(rs []rune) bool {
	if len(rs) == 0 {
		return false
	}
	var rec func(int) bool
	rec = func(i int) bool {
		if i == len(rs) {
			return true
		}
		if i+1 < len(rs) && rs[i] >= 'A' && rs[i] <= 'Z' && rs[i+1] == '.' {
			if rec(i + 2) {
				return true
			}
		}
		if i+2 < len(rs) && rs[i] >= 'A' && rs[i] <= 'Z' && rs[i+1] == '.' && rs[i+2] >= 'A' && rs[i+2] <= 'Z' {
			if rec(i + 3) {
				return true
			}
		}
		return false
	}
	return rec(0)
}

func matchApos(rs []rune) bool {
	if len(rs) < 3 || !isDOL(rs[0]) {
		return false
	}
	if rs[1] != '\'' && rs[1] != '\u2018' {
		return false
	}
	rest := rs[2:]
	if len(rest) >= 1 && allWord(rest) {
		return true
	}
	if len(rest) >= 3 && isAposSuffix(rest[len(rest)-2]) && isAposSuffix(rest[len(rest)-1]) && allWord(rest[:len(rest)-2]) {
		return true
	}
	return false
}

func isDOL(r rune) bool {
	switch unicode.ToLower(r) {
	case 'd', 'o', 'l':
		return true
	}
	return false
}

func isAposSuffix(r rune) bool {
	return r == '\'' || r == 's' || r == 'S'
}

func allWord(rs []rune) bool {
	if len(rs) == 0 {
		return false
	}
	for _, r := range rs {
		if !isWordRune(r) {
			return false
		}
	}
	return true
}

func applyApos(word string) string {
	rs := []rune(word)
	var first string
	if isVowel(rs[0]) {
		first = strings.ToUpper(string(rs[0]))
	} else {
		first = strings.ToLower(string(rs[0]))
	}
	return first + string(rs[1]) + strings.ToUpper(string(rs[2])) + string(rs[3:])
}

func isVowel(r rune) bool {
	switch r {
	case 'a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U':
		return true
	}
	return false
}

func splitMc(word string) (prefix, rest string, ok bool) {
	rs := []rune(word)
	if len(rs) < 4 {
		return "", "", false
	}
	if (rs[0] == 'M' || rs[0] == 'm') && rs[1] == 'c' && isWordRune(rs[2]) {
		return string(rs[:2]), string(rs[2:]), true
	}
	if rs[0] == 'M' && rs[1] == 'C' && isWordRune(rs[2]) {
		return string(rs[:2]), string(rs[2:]), true
	}
	return "", "", false
}

func matchMr(word string) bool {
	switch strings.ToLower(word) {
	case "mr", "mrs", "ms", "dr":
		return true
	}
	return false
}
ENDGO

find . -type f -name '*.py' -delete
# go build ./... names its binary after the module, titlecase, and will not
# replace a directory of that name left behind by the Python package.
rm -rf titlecase
