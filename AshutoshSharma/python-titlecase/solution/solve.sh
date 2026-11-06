#!/bin/bash
# Port the original Python titlecase() function to Go and remove the Python sources.
set -euo pipefail

repo=/workspace/repo
mkdir -p "$repo"

cat > "$repo/go.mod" << 'EOF'
module titlecase

go 1.23
EOF

cat > "$repo/main.go" << 'EOF'
package main

import (
	"io"
	"os"
	"strings"
	"unicode"
	"unicode/utf8"
)

// titlecase is the default-argument behaviour of the Python titlecase()
// function. Word boundaries are checked by hand: the Python patterns use \b,
// and Go's regexp engine has no look-ahead or look-behind to express that.
func main() {
	in, err := io.ReadAll(os.Stdin)
	if err != nil {
		os.Exit(1)
	}
	os.Stdout.WriteString(titlecase(string(in), true))
}

func titlecase(text string, smallFirstLast bool) string {
	lines := splitLines(text)
	out := make([]string, len(lines))
	for i, line := range lines {
		out[i] = processLine(line, smallFirstLast)
	}
	return strings.Join(out, "\n")
}

func splitLines(text string) []string {
	if text == "" {
		return []string{""}
	}
	var lines []string
	var cur strings.Builder
	for i := 0; i < len(text); i++ {
		if text[i] == '\r' || text[i] == '\n' {
			lines = append(lines, cur.String())
			cur.Reset()
			for i+1 < len(text) && (text[i+1] == '\r' || text[i+1] == '\n') {
				i++
			}
			continue
		}
		cur.WriteByte(text[i])
	}
	lines = append(lines, cur.String())
	return lines
}

func processLine(line string, smallFirstLast bool) string {
	allCaps := strings.ToUpper(line) == line
	words, spaces := splitSpaces(line)
	tc := make([]string, len(words))
	for i, word := range words {
		tc[i] = titleWord(word, allCaps)
	}
	if smallFirstLast && len(tc) > 0 {
		tc[0] = applySmallFirst(tc[0])
		tc[len(tc)-1] = applySmallLast(tc[len(tc)-1])
	}
	joined := interleave(tc, spaces)
	return applySubphrase(joined)
}

func splitSpaces(line string) (words, spaces []string) {
	var cur strings.Builder
	for _, r := range line {
		if unicode.IsSpace(r) {
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

func interleave(words, spaces []string) string {
	var b strings.Builder
	for i, word := range words {
		b.WriteString(word)
		if i < len(spaces) {
			b.WriteString(spaces[i])
		}
	}
	return b.String()
}

func titleWord(word string, allCaps bool) string {
	if allCaps && isInitials(word) {
		return word
	}
	if shaped, ok := apostropheName(word); ok {
		return shaped
	}
	if prefix, rest, ok := macPrefix(word); ok {
		return capitalize(prefix) + titlecase(rest, true)
	}
	if isHonorific(word) {
		return upperFirst(word)
	}
	if hasInlinePeriod(word) || (!allCaps && hasUpperLater(word)) {
		return word
	}
	if isSmallWord(word) {
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
	}
	if runeLen(word) > 2 && isAllConsonants(word) {
		return strings.ToUpper(word)
	}
	return capFirst(word)
}

func isInitials(s string) bool {
	rs := []rune(s)
	if len(rs) == 0 {
		return false
	}
	var rec func(int) bool
	rec = func(i int) bool {
		if i == len(rs) {
			return true
		}
		// An initials token is a run of "A." or "A.B" pieces.
		if i+1 < len(rs) && isUpperLetter(rs[i]) && rs[i+1] == '.' {
			if rec(i + 2) {
				return true
			}
			if i+2 < len(rs) && isUpperLetter(rs[i+2]) && rec(i+3) {
				return true
			}
		}
		return false
	}
	return rec(0)
}

func apostropheName(word string) (string, bool) {
	rs := []rune(word)
	if len(rs) < 3 || !isDOL(rs[0]) {
		return "", false
	}
	if rs[1] != '\'' && rs[1] != '\u2018' {
		return "", false
	}
	body := rs[2:]
	letterEnd := len(body)
	if len(body) >= 3 && isAposSuffix(body[len(body)-2]) && isAposSuffix(body[len(body)-1]) && allLetters(body[:len(body)-2]) {
		letterEnd = len(body) - 2
	}
	if letterEnd < 1 || !allLetters(body[:letterEnd]) {
		return "", false
	}
	var b strings.Builder
	if isAposVowel(rs[0]) {
		b.WriteString(strings.ToUpper(string(rs[0])))
	} else {
		b.WriteString(strings.ToLower(string(rs[0])))
	}
	b.WriteRune(rs[1])
	b.WriteString(strings.ToUpper(string(rs[2])))
	b.WriteString(string(rs[3:]))
	return b.String(), true
}

func isDOL(r rune) bool {
	switch r {
	case 'd', 'D', 'o', 'O', 'l', 'L':
		return true
	default:
		return false
	}
}

func isAposVowel(r rune) bool {
	switch r {
	case 'a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U':
		return true
	default:
		return false
	}
}

func isAposSuffix(r rune) bool {
	return r == '\'' || r == 's' || r == 'S'
}

func allLetters(rs []rune) bool {
	if len(rs) == 0 {
		return false
	}
	for _, r := range rs {
		if !unicode.IsLetter(r) {
			return false
		}
	}
	return true
}

func macPrefix(word string) (prefix, rest string, ok bool) {
	rs := []rune(word)
	if len(rs) < 4 {
		return "", "", false
	}
	mc := (rs[0] == 'M' || rs[0] == 'm') && rs[1] == 'c'
	upperMC := rs[0] == 'M' && rs[1] == 'C'
	if !mc && !upperMC {
		return "", "", false
	}
	tail := rs[2:]
	if len(tail) >= 2 && isWord(tail[0]) {
		return string(rs[:2]), string(tail), true
	}
	return "", "", false
}

func isHonorific(s string) bool {
	switch strings.ToLower(s) {
	case "mr", "mrs", "ms", "dr":
		return true
	default:
		return false
	}
}

func hasInlinePeriod(s string) bool {
	rs := []rune(s)
	for i := 0; i+2 < len(rs); i++ {
		if unicode.IsLetter(rs[i]) && rs[i+1] == '.' && unicode.IsLetter(rs[i+2]) {
			return true
		}
	}
	return false
}

func hasUpperLater(s string) bool {
	rs := []rune(s)
	i := 0
	for i < len(rs) && isPunct(rs[i]) {
		i++
	}
	if i >= len(rs) || !unicode.IsLetter(rs[i]) {
		return false
	}
	j := i
	for j < len(rs) && unicode.IsLetter(rs[j]) {
		j++
	}
	for k := i + 1; k < j; k++ {
		if isUpperLetter(rs[k]) {
			return true
		}
	}
	return false
}

func isSmallWord(s string) bool {
	switch strings.ToLower(s) {
	case "a", "an", "and", "as", "at", "but", "by", "en", "for", "if", "in",
		"of", "on", "or", "the", "to", "v", "v.", "via", "vs", "vs.":
		return true
	default:
		return false
	}
}

func isAllConsonants(s string) bool {
	if s == "" {
		return false
	}
	for _, r := range s {
		if r >= 'A' && r <= 'Z' {
			r = r - 'A' + 'a'
		}
		switch r {
		case 'b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z':
		default:
			return false
		}
	}
	return true
}

func capFirst(s string) string {
	rs := []rune(s)
	for i, r := range rs {
		if isPunct(r) {
			continue
		}
		if unicode.IsLetter(r) {
			rs[i] = unicode.ToUpper(r)
			return string(rs)
		}
		return s
	}
	return s
}

func applySmallFirst(s string) string {
	rs := []rune(s)
	i := 0
	for i < len(rs) && isPunct(rs[i]) {
		i++
	}
	n, ok := matchSmallBounded(rs, i)
	if !ok {
		return s
	}
	return string(rs[:i]) + capitalize(string(rs[i:i+n])) + string(rs[i+n:])
}

func applySmallLast(s string) string {
	rs := []rune(s)
	start, ok := matchSmallLast(rs)
	if !ok {
		return s
	}
	return string(rs[:start]) + capitalize(string(rs[start:]))
}

func matchSmallBounded(rs []rune, at int) (int, bool) {
	rest := rs[at:]
	for _, lit := range smallLiterals {
		n := len([]rune(lit))
		if hasPrefixFold(rest, lit) && isBoundary(rs, at+n) {
			return n, true
		}
	}
	if len(rest) > 0 && eqV(rest[0]) {
		if len(rest) > 1 && rest[1] == '.' && isBoundary(rs, at+2) {
			return 2, true
		}
		if isBoundary(rs, at+1) {
			return 1, true
		}
	}
	if hasPrefixFold(rest, "via") && isBoundary(rs, at+3) {
		return 3, true
	}
	if len(rest) >= 2 && strings.EqualFold(string(rest[:2]), "vs") {
		if len(rest) > 2 && rest[2] == '.' && isBoundary(rs, at+3) {
			return 3, true
		}
		if isBoundary(rs, at+2) {
			return 2, true
		}
	}
	return 0, false
}

func matchSmallLast(rs []rune) (int, bool) {
	if len(rs) == 0 {
		return 0, false
	}
	var punctLens []int
	if isPunct(rs[len(rs)-1]) {
		punctLens = append(punctLens, 1)
	}
	punctLens = append(punctLens, 0)
	for _, plen := range punctLens {
		wordEnd := len(rs) - plen
		if start, ok := smallSuffix(rs[:wordEnd]); ok {
			return start, true
		}
	}
	return 0, false
}

func smallSuffix(rs []rune) (int, bool) {
	for _, lit := range smallLiterals {
		n := len([]rune(lit))
		if len(rs) >= n && strings.EqualFold(string(rs[len(rs)-n:]), lit) && isBoundary(rs, len(rs)-n) {
			return len(rs) - n, true
		}
	}
	if len(rs) >= 2 && eqV(rs[len(rs)-2]) && rs[len(rs)-1] == '.' && isBoundary(rs, len(rs)-2) {
		return len(rs) - 2, true
	}
	if len(rs) >= 1 && eqV(rs[len(rs)-1]) && isBoundary(rs, len(rs)-1) {
		return len(rs) - 1, true
	}
	if len(rs) >= 3 && strings.EqualFold(string(rs[len(rs)-3:]), "via") && isBoundary(rs, len(rs)-3) {
		return len(rs) - 3, true
	}
	if len(rs) >= 3 && strings.EqualFold(string(rs[len(rs)-3:len(rs)-1]), "vs") && rs[len(rs)-1] == '.' && isBoundary(rs, len(rs)-3) {
		return len(rs) - 3, true
	}
	if len(rs) >= 2 && strings.EqualFold(string(rs[len(rs)-2:]), "vs") && isBoundary(rs, len(rs)-2) {
		return len(rs) - 2, true
	}
	return 0, false
}

func applySubphrase(s string) string {
	rs := []rune(s)
	var b strings.Builder
	for i := 0; i < len(rs); {
		if i+1 < len(rs) && isSubPunct(rs[i]) && rs[i+1] == ' ' {
			if n := matchSmallExact(rs[i+2:]); n > 0 {
				b.WriteRune(rs[i])
				b.WriteRune(' ')
				b.WriteString(capitalize(string(rs[i+2 : i+2+n])))
				i += 2 + n
				continue
			}
		}
		b.WriteRune(rs[i])
		i++
	}
	return b.String()
}

// matchSmallExact follows the Python subphrase alternation. It is
// case-sensitive, has no word-boundary check, and stops at the first hit,
// so "v" wins over "via" and "vs".
func matchSmallExact(rs []rune) int {
	for _, lit := range smallLiterals {
		n := len([]rune(lit))
		if len(rs) >= n && string(rs[:n]) == lit {
			return n
		}
	}
	if len(rs) > 0 && rs[0] == 'v' {
		if len(rs) > 1 && rs[1] == '.' {
			return 2
		}
		return 1
	}
	if len(rs) >= 3 && string(rs[:3]) == "via" {
		return 3
	}
	if len(rs) >= 2 && rs[0] == 'v' && rs[1] == 's' {
		if len(rs) > 2 && rs[2] == '.' {
			return 3
		}
		return 2
	}
	return 0
}

var smallLiterals = []string{
	"a", "an", "and", "as", "at", "but", "by", "en", "for", "if", "in", "of", "on", "or", "the", "to",
}

func hasPrefixFold(rs []rune, lit string) bool {
	lr := []rune(lit)
	if len(rs) < len(lr) {
		return false
	}
	return strings.EqualFold(string(rs[:len(lr)]), lit)
}

func eqV(r rune) bool {
	return r == 'v' || r == 'V'
}

func isBoundary(rs []rune, i int) bool {
	left := i > 0 && isWord(rs[i-1])
	right := i < len(rs) && isWord(rs[i])
	return left != right
}

func isWord(r rune) bool {
	if unicode.IsLetter(r) || unicode.IsMark(r) {
		return true
	}
	return unicode.In(r, unicode.Nd, unicode.Nl, unicode.Pc)
}

func isUpperLetter(r rune) bool {
	return unicode.Is(unicode.Lu, r)
}

func isPunct(r rune) bool {
	switch r {
	case '!', '"', '#', '$', '%', '&', '\'', '(', ')', '*', '+', ',', '-', '.', '/',
		':', ';', '?', '@', '[', '\\', ']', '_', '`', '{', '|', '}', '~',
		'\u2012', '\u2013', '\u2014', '\u2015', '\u2018', '\u201c':
		return true
	default:
		return false
	}
}

func isSubPunct(r rune) bool {
	switch r {
	case ':', '.', ';', '?', '!', '-', '\u2012', '\u2013', '\u2014', '\u2015':
		return true
	default:
		return false
	}
}

func upperFirst(s string) string {
	r, size := utf8.DecodeRuneInString(s)
	if size == 0 {
		return s
	}
	return string(unicode.ToUpper(r)) + s[size:]
}

func capitalize(s string) string {
	r, size := utf8.DecodeRuneInString(s)
	if size == 0 {
		return s
	}
	return string(unicode.ToUpper(r)) + strings.ToLower(s[size:])
}

func runeLen(s string) int {
	return utf8.RuneCountInString(s)
}
EOF

find "$repo" -type f -name '*.py' -delete
