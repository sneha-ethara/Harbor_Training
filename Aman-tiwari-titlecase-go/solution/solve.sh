#!/bin/bash
# Reference solution (oracle): write a Go port of python-titlecase into
# /workspace/repo (go.mod + main.go, standard library only), then delete
# every .py file and the rest of the Python packaging.
set -euo pipefail
cd /workspace/repo

cat > go.mod <<'EOF_GOMOD'
module github.com/ppannuto/titlecase-go

go 1.23
EOF_GOMOD

cat > main.go <<'EOF_GO'
// Command titlecase is a Go port of python-titlecase 2.4.1 (plain install,
// Python's built-in `re`, default arguments). It reads one title per line on
// stdin and writes the titlecased line to stdout.
//
// Go's regexp has no look-around or back-references and its \b and \w are
// ASCII-only, so every Python pattern is rebuilt here as plain string code.
package main

import (
	"bufio"
	"io"
	"os"
	"strings"
	"unicode"
)

// ---------------------------------------------------------------- character classes

// PUNCT = !"“#$%&'‘()*+,\-–‒—―./:;?@[\\\]_`{|}~
const punctChars = "!\"“#$%&'‘()*+,-–‒—―./:;?@[\\]_`{|}~"

func isPunct(r rune) bool { return strings.ContainsRune(punctChars, r) }

// SUBPHRASE separators: [:.;?!\-–‒—―]
func isSubphraseSep(r rune) bool { return strings.ContainsRune(":.;?!-–‒—―", r) }

// Python's Unicode \w: letters, numbers (str.isalnum) and underscore.
func isWord(r rune) bool { return r == '_' || unicode.IsLetter(r) || unicode.IsNumber(r) }

// Python's Unicode \s (str.isspace).
func isSpace(r rune) bool { return unicode.IsSpace(r) || (r >= 0x1c && r <= 0x1f) }

func isASCIILetter(r rune) bool { return (r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') }

// ---------------------------------------------------------------- Python case mapping

// Full upper-case mappings that are more than one character (SpecialCasing.txt).
var specialUpper = map[rune]string{
	'ß': "SS", 'ŉ': "ʼN", 'ǰ': "J̌", 'ΐ': "Ϊ́", 'ΰ': "Ϋ́", 'և': "ԵՒ",
	'ẖ': "H̱", 'ẗ': "T̈", 'ẘ': "W̊", 'ẙ': "Y̊", 'ẚ': "Aʾ",
	'ﬀ': "FF", 'ﬁ': "FI", 'ﬂ': "FL", 'ﬃ': "FFI", 'ﬄ': "FFL", 'ﬅ': "ST", 'ﬆ': "ST",
	'ﬓ': "ՄՆ", 'ﬔ': "ՄԵ", 'ﬕ': "ՄԻ", 'ﬖ': "ՎՆ", 'ﬗ': "ՄԽ",
}

func upperRune(r rune) string {
	if s, ok := specialUpper[r]; ok {
		return s
	}
	return string(unicode.ToUpper(r))
}

func lowerRune(r rune) string {
	if r == 'İ' {
		return "i̇"
	}
	return string(unicode.ToLower(r))
}

func pyUpper(s string) string {
	var b strings.Builder
	for _, r := range s {
		b.WriteString(upperRune(r))
	}
	return b.String()
}

func isCased(r rune) bool {
	return unicode.IsUpper(r) || unicode.IsLower(r) || unicode.IsTitle(r)
}

// Case-ignorable characters (approximation used for the Greek final sigma rule).
func isCaseIgnorable(r rune) bool {
	return unicode.In(r, unicode.Mn, unicode.Me, unicode.Cf, unicode.Lm, unicode.Sk) ||
		r == '\'' || r == '.' || r == ':' || r == '^' || r == '`' || r == '·' || r == '’'
}

// pyLower mirrors str.lower(), including the Greek final-sigma rule.
func pyLower(s string) string {
	rs := []rune(s)
	var b strings.Builder
	for i, r := range rs {
		if r == 'Σ' && finalSigma(rs, i) {
			b.WriteRune('ς')
			continue
		}
		b.WriteString(lowerRune(r))
	}
	return b.String()
}

func finalSigma(rs []rune, i int) bool {
	before := false
	for j := i - 1; j >= 0; j-- {
		if isCaseIgnorable(rs[j]) {
			continue
		}
		before = isCased(rs[j])
		break
	}
	if !before {
		return false
	}
	for j := i + 1; j < len(rs); j++ {
		if isCaseIgnorable(rs[j]) {
			continue
		}
		return !isCased(rs[j])
	}
	return true
}

// pyCapitalize mirrors str.capitalize(): first char title-cased, rest lower.
func pyCapitalize(s string) string {
	rs := []rune(s)
	if len(rs) == 0 {
		return s
	}
	var first string
	if up, ok := specialUpper[rs[0]]; ok {
		// Title case of these is the upper form with the rest lowered.
		ur := []rune(up)
		first = string(ur[0]) + strings.ToLower(string(ur[1:]))
	} else {
		first = string(unicode.ToTitle(rs[0]))
	}
	return first + pyLower(string(rs[1:]))
}

// ---------------------------------------------------------------- small words

// SMALL alternatives, in regex order: a|an|and|as|at|but|by|en|for|if|in|of|on|or|the|to|v\.?|via|vs\.?
// "v\.?" and "vs\.?" are expanded greedy-first ("v." before "v").
var smallAlts = []string{"a", "an", "and", "as", "at", "but", "by", "en", "for", "if",
	"in", "of", "on", "or", "the", "to", "v.", "v", "via", "vs.", "vs"}

// hasPrefixFold reports whether rs[i:] starts with alt (case-insensitive) and
// returns the number of runes matched.
func hasPrefixFold(rs []rune, i int, alt string) (int, bool) {
	ar := []rune(alt)
	if i+len(ar) > len(rs) {
		return 0, false
	}
	if !strings.EqualFold(string(rs[i:i+len(ar)]), alt) {
		return 0, false
	}
	return len(ar), true
}

func hasPrefixExact(rs []rune, i int, alt string) (int, bool) {
	ar := []rune(alt)
	if i+len(ar) > len(rs) {
		return 0, false
	}
	if string(rs[i:i+len(ar)]) != alt {
		return 0, false
	}
	return len(ar), true
}

// isBoundary mirrors Python's \b at position i of rs (Unicode \w).
func isBoundary(rs []rune, i int) bool {
	before := i > 0 && isWord(rs[i-1])
	after := i < len(rs) && isWord(rs[i])
	return before != after
}

// SMALL_WORDS = ^(SMALL)$, IGNORECASE
func isSmallWord(w string) bool {
	for _, alt := range smallAlts {
		if strings.EqualFold(w, alt) {
			return true
		}
	}
	return false
}

// SMALL_FIRST = ^([PUNCT]*)(SMALL)\b, IGNORECASE; replace with g1 + g2.capitalize()
func smallFirst(w string) string {
	rs := []rune(w)
	p := 0
	for p < len(rs) && isPunct(rs[p]) {
		p++
	}
	for _, alt := range smallAlts {
		n, ok := hasPrefixFold(rs, p, alt)
		if ok && isBoundary(rs, p+n) {
			return string(rs[:p]) + pyCapitalize(string(rs[p:p+n])) + string(rs[p+n:])
		}
	}
	return w
}

// SMALL_LAST = \b(SMALL)[PUNCT]?$, IGNORECASE; replace group(0) with group(0).capitalize()
func smallLast(w string) string {
	rs := []rune(w)
	for p := 0; p <= len(rs); p++ {
		if !isBoundary(rs, p) {
			continue
		}
		for _, alt := range smallAlts {
			n, ok := hasPrefixFold(rs, p, alt)
			if !ok {
				continue
			}
			rest := rs[p+n:]
			if len(rest) == 0 || (len(rest) == 1 && isPunct(rest[0])) {
				return string(rs[:p]) + pyCapitalize(string(rs[p:]))
			}
		}
	}
	return w
}

// SUBPHRASE = ([:.;?!\-–‒—―][ ])(SMALL)  (case-sensitive, no \b);
// replace with g1 + g2.capitalize(), for every non-overlapping match.
func subphrase(s string) string {
	rs := []rune(s)
	var b strings.Builder
	i := 0
	for i < len(rs) {
		if i+1 < len(rs) && isSubphraseSep(rs[i]) && rs[i+1] == ' ' {
			matched := false
			for _, alt := range smallAlts {
				if n, ok := hasPrefixExact(rs, i+2, alt); ok {
					b.WriteRune(rs[i])
					b.WriteRune(' ')
					b.WriteString(pyCapitalize(string(rs[i+2 : i+2+n])))
					i += 2 + n
					matched = true
					break
				}
			}
			if matched {
				continue
			}
		}
		b.WriteRune(rs[i])
		i++
	}
	return b.String()
}

// ---------------------------------------------------------------- word patterns

// UC_INITIALS = ^(?:[A-Z]\.|[A-Z]\.[A-Z])+$
func ucInitials(rs []rune, i int) bool {
	if i == len(rs) {
		return false
	}
	return ucInitialsRest(rs, i)
}

func ucInitialsRest(rs []rune, i int) bool {
	if i == len(rs) {
		return true
	}
	isUp := func(j int) bool { return j < len(rs) && rs[j] >= 'A' && rs[j] <= 'Z' }
	if isUp(i) && i+1 < len(rs) && rs[i+1] == '.' {
		if ucInitialsRest(rs, i+2) {
			return true
		}
		if isUp(i+2) && ucInitialsRest(rs, i+3) {
			return true
		}
	}
	return false
}

// APOS_SECOND = ^[dol]['‘][\w]+(?:['s]{2})?$, IGNORECASE
func aposSecond(rs []rune) bool {
	if len(rs) < 3 {
		return false
	}
	switch rs[0] {
	case 'd', 'o', 'l', 'D', 'O', 'L':
	default:
		return false
	}
	if rs[1] != '\'' && rs[1] != '‘' {
		return false
	}
	rest := rs[2:]
	allWord := func(x []rune) bool {
		if len(x) == 0 {
			return false
		}
		for _, r := range x {
			if !isWord(r) {
				return false
			}
		}
		return true
	}
	if allWord(rest) {
		return true
	}
	isQS := func(r rune) bool { return r == '\'' || r == 's' || r == 'S' }
	n := len(rest)
	return n >= 3 && allWord(rest[:n-2]) && isQS(rest[n-2]) && isQS(rest[n-1])
}

// MAC_MC = ^([Mm]c|MC)(\w.+)
func macMc(rs []rune) (string, string, bool) {
	if len(rs) < 4 {
		return "", "", false
	}
	pre := string(rs[:2])
	if pre != "Mc" && pre != "mc" && pre != "MC" {
		return "", "", false
	}
	if !isWord(rs[2]) {
		return "", "", false
	}
	return pre, string(rs[2:]), true
}

// MR_MRS_MS_DR = ^((m((rs?)|s))|Dr)$, IGNORECASE
func mrMrsMsDr(w string) bool {
	switch strings.ToLower(w) {
	case "mr", "mrs", "ms", "dr":
		return true
	}
	return false
}

// INLINE_PERIOD = [\w][.][\w] (search)
func inlinePeriod(rs []rune) bool {
	for i := 0; i+2 < len(rs); i++ {
		if isWord(rs[i]) && rs[i+1] == '.' && isWord(rs[i+2]) {
			return true
		}
	}
	return false
}

// UC_ELSEWHERE = [PUNCT]*?[a-zA-Z]+[A-Z]+? (match at start)
func ucElsewhere(rs []rune) bool {
	k := 0
	for k < len(rs) && isPunct(rs[k]) {
		k++
	}
	if k >= len(rs) || !isASCIILetter(rs[k]) {
		return false
	}
	for j := k + 1; j < len(rs) && isASCIILetter(rs[j]); j++ {
		if rs[j] >= 'A' && rs[j] <= 'Z' {
			return true
		}
	}
	return false
}

// is_all_consonants = \A[bcdfghjklmnpqrstvwxz]+\Z, IGNORECASE
func allConsonants(rs []rune) bool {
	if len(rs) == 0 {
		return false
	}
	for _, r := range rs {
		switch r {
		case 'ſ': // folds to 's'
			continue
		case 'K': // Kelvin sign folds to 'k'
			continue
		}
		if !strings.ContainsRune("bcdfghjklmnpqrstvwxz", unicode.ToLower(r)) || r > unicode.MaxASCII {
			return false
		}
	}
	return true
}

// CAPFIRST = ^[PUNCT]*?([\w]); replace group(0) with group(0).upper()
func capFirst(rs []rune) string {
	for i, r := range rs {
		if isWord(r) {
			return string(rs[:i]) + upperRune(r) + string(rs[i+1:])
		}
		if !isPunct(r) {
			break
		}
	}
	return string(rs)
}

// ---------------------------------------------------------------- titlecase

// splitSpaces mirrors re.split(r'(\s)', line): words and the single
// whitespace characters between them.
func splitSpaces(line string) (words []string, spaces []string) {
	start := 0
	for i, r := range line {
		if isSpace(r) {
			words = append(words, line[start:i])
			spaces = append(spaces, string(r))
			start = i + len(string(r))
		}
	}
	words = append(words, line[start:])
	return
}

// splitLines mirrors re.split('[\r\n]+', text).
func splitLines(text string) []string {
	var out []string
	start := 0
	i := 0
	for i < len(text) {
		if text[i] == '\r' || text[i] == '\n' {
			out = append(out, text[start:i])
			for i < len(text) && (text[i] == '\r' || text[i] == '\n') {
				i++
			}
			start = i
			continue
		}
		i++
	}
	return append(out, text[start:])
}

func titlecaseWord(word string, allCaps bool) string {
	rs := []rune(word)

	if allCaps && ucInitials(rs, 0) {
		return word
	}

	if aposSecond(rs) {
		var first string
		if !strings.ContainsRune("aeiouAEIOU", rs[0]) {
			first = pyLower(string(rs[0]))
		} else {
			first = upperRune(rs[0])
		}
		return first + string(rs[1]) + upperRune(rs[2]) + string(rs[3:])
	}

	if pre, rest, ok := macMc(rs); ok {
		return pyCapitalize(pre) + titlecase(rest, true)
	}

	if mrMrsMsDr(word) {
		return upperRune(rs[0]) + string(rs[1:])
	}

	if inlinePeriod(rs) || (!allCaps && ucElsewhere(rs)) {
		return word
	}

	if isSmallWord(word) {
		return pyLower(word)
	}

	if strings.Contains(word, "/") && !strings.Contains(word, "//") {
		parts := strings.Split(word, "/")
		for i, p := range parts {
			parts[i] = titlecase(p, false)
		}
		return strings.Join(parts, "/")
	}

	if strings.Contains(word, "-") {
		parts := strings.Split(word, "-")
		for i, p := range parts {
			parts[i] = titlecase(p, false)
		}
		return strings.Join(parts, "-")
	}

	if allCaps {
		word = pyLower(word)
		rs = []rune(word)
	}

	if allConsonants(rs) && len(rs) > 2 {
		return pyUpper(word)
	}

	return capFirst(rs)
}

func titlecase(text string, smallFirstLast bool) string {
	lines := splitLines(text)
	processed := make([]string, 0, len(lines))
	for _, line := range lines {
		allCaps := pyUpper(line) == line
		words, spaces := splitSpaces(line)
		tc := make([]string, len(words))
		for i, w := range words {
			tc[i] = titlecaseWord(w, allCaps)
		}

		if smallFirstLast && len(tc) > 0 {
			tc[0] = smallFirst(tc[0])
			tc[len(tc)-1] = smallLast(tc[len(tc)-1])
		}

		var b strings.Builder
		for i, w := range tc {
			b.WriteString(w)
			if i < len(spaces) {
				b.WriteString(spaces[i])
			}
		}
		processed = append(processed, subphrase(b.String()))
	}
	return strings.Join(processed, "\n")
}

func main() {
	in := bufio.NewReaderSize(os.Stdin, 1<<16)
	out := bufio.NewWriterSize(os.Stdout, 1<<16)
	defer out.Flush()
	for {
		line, err := in.ReadString('\n')
		if len(line) > 0 {
			line = strings.TrimSuffix(line, "\n")
			out.WriteString(titlecase(line, true))
			out.WriteByte('\n')
		}
		if err == io.EOF {
			break
		}
		if err != nil {
			os.Exit(1)
		}
	}
}
EOF_GO

# The Python machine is gone: remove all Python files and packaging.
find . -name '*.py' -type f -delete
find . -name '__pycache__' -type d -prune -exec rm -rf {} +
rm -rf titlecase setup.cfg pyproject.toml tox.ini

gofmt -l . || true
go build ./...
echo "solve.sh: Go port written, Python removed, go build ./... OK"
