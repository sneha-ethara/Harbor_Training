package main

import (
	"strings"
	"unicode"
	"unicode/utf8"
)

// processLine is the default titlecase() path: no callback, and the caller's
// smallFirstLast flag. Recursive Mc / slash / hyphen calls pass false so a
// small word inside a compound is not capitalized, while the outer line still
// capitalizes its own first and last words afterwards.
func processLine(line string, smallFirstLast bool) string {
	allCaps := pyUpper(line) == line
	words, spaces := splitSpace(line)
	out := make([]string, len(words))
	for i, word := range words {
		out[i] = processWord(word, allCaps)
	}
	if smallFirstLast && len(out) > 0 {
		out[0] = applySmallFirst(out[0])
		out[len(out)-1] = applySmallLast(out[len(out)-1])
	}
	return applySubphrase(joinSpace(out, spaces))
}

func processWord(word string, allCaps bool) string {
	if allCaps && ucInitials(word) {
		return word
	}
	if rewritten, ok := aposSecond(word); ok {
		return rewritten
	}
	if rewritten, ok := macMC(word); ok {
		return rewritten
	}
	if rewritten, ok := honorific(word); ok {
		return rewritten
	}
	if inlinePeriod(word) || (!allCaps && ucElsewhere(word)) {
		return word
	}
	if smallWord(word) {
		return pyLower(word)
	}
	if strings.Contains(word, "/") && !strings.Contains(word, "//") {
		parts := strings.Split(word, "/")
		for i, part := range parts {
			parts[i] = processLine(part, false)
		}
		return strings.Join(parts, "/")
	}
	if strings.Contains(word, "-") {
		parts := strings.Split(word, "-")
		for i, part := range parts {
			parts[i] = processLine(part, false)
		}
		return strings.Join(parts, "-")
	}
	if allCaps {
		word = pyLower(word)
	}
	if n := len([]rune(word)); n > 2 && allConsonants(word) {
		return pyUpper(word)
	}
	return capFirst(word)
}

// Python re.split(r'(\s)', line), one whitespace character at a time.
func splitSpace(line string) (words, spaces []string) {
	start := 0
	for i, r := range line {
		if !isPySpace(r) {
			continue
		}
		n := utf8.RuneLen(r)
		words = append(words, line[start:i])
		spaces = append(spaces, line[i:i+n])
		start = i + n
	}
	words = append(words, line[start:])
	return words, spaces
}

func joinSpace(words, spaces []string) string {
	var b strings.Builder
	for i, word := range words {
		b.WriteString(word)
		if i < len(spaces) {
			b.WriteString(spaces[i])
		}
	}
	return b.String()
}

// ^(?:[A-Z]\.|[A-Z]\.[A-Z])+$ with the same left-first backtracking as re.
func ucInitials(s string) bool {
	if s == "" {
		return false
	}
	for i := 0; i < len(s); i++ {
		c := s[i]
		if c != '.' && (c < 'A' || c > 'Z') {
			return false
		}
	}
	return matchInitials(s, 0)
}

func matchInitials(s string, i int) bool {
	if i == len(s) {
		return true
	}
	if i+2 <= len(s) && s[i] >= 'A' && s[i] <= 'Z' && s[i+1] == '.' {
		if matchInitials(s, i+2) {
			return true
		}
	}
	if i+3 <= len(s) && s[i] >= 'A' && s[i] <= 'Z' && s[i+1] == '.' && s[i+2] >= 'A' && s[i+2] <= 'Z' {
		if matchInitials(s, i+3) {
			return true
		}
	}
	return false
}

// ^[dol]['‘][\w]+(?:['s]{2})?$ under re.I. The letter after the apostrophe
// is uppercased; a leading o is uppercased and a leading d or l is lowercased.
// Everything after that letter is kept.
func aposSecond(word string) (string, bool) {
	rs := []rune(word)
	if len(rs) < 3 || !isDOL(rs[0]) || (rs[1] != '\'' && rs[1] != '\u2018') {
		return "", false
	}
	if !aposBody(rs[2:]) {
		return "", false
	}
	var first rune
	if strings.ContainsRune("aeiouAEIOU", rs[0]) {
		first = unicode.ToUpper(rs[0])
	} else {
		first = unicode.ToLower(rs[0])
	}
	var b strings.Builder
	b.WriteRune(first)
	b.WriteRune(rs[1])
	b.WriteString(pyUpper(string(rs[2:3])))
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

func aposBody(body []rune) bool {
	if len(body) == 0 {
		return false
	}
	n := 0
	for n < len(body) && isWord(body[n]) {
		n++
	}
	if n == len(body) {
		return true
	}
	return n >= 1 && len(body)-n == 2 && isAposSuffix(body[n]) && isAposSuffix(body[n+1])
}

func isAposSuffix(r rune) bool {
	return r == '\'' || r == 's' || r == 'S' || r == 'ſ'
}

// ^([Mm]c|MC)(\w.+). The remainder is title-cased with small words at its
// own ends capitalized. A newline stops the match, as Python's '.' does,
// and the unmatched tail is not copied.
func macMC(word string) (string, bool) {
	rs := []rune(word)
	if len(rs) < 4 {
		return "", false
	}
	mc := (rs[0] == 'M' || rs[0] == 'm') && rs[1] == 'c'
	upperMC := rs[0] == 'M' && rs[1] == 'C'
	if !mc && !upperMC {
		return "", false
	}
	if !isWord(rs[2]) {
		return "", false
	}
	end := 3
	for end < len(rs) && rs[end] != '\n' && rs[end] != '\r' {
		end++
	}
	if end < 4 {
		return "", false
	}
	return pyCapitalize(string(rs[:2])) + processLine(string(rs[2:end]), true), true
}

// ^((m((rs?)|s))|Dr)$ under re.I. Bare "m" does not match. The first
// character is uppercased and the rest is kept.
func honorific(word string) (string, bool) {
	switch foldASCII(word) {
	case "mr", "mrs", "ms", "dr":
	default:
		return "", false
	}
	rs := []rune(word)
	return pyUpper(string(rs[:1])) + string(rs[1:]), true
}

func inlinePeriod(word string) bool {
	rs := []rune(word)
	for i := 0; i+2 < len(rs); i++ {
		if isWord(rs[i]) && rs[i+1] == '.' && isWord(rs[i+2]) {
			return true
		}
	}
	return false
}

// [%punct]*?[A-Za-z]+[A-Z]+  from the start of the word. The letter run is
// ASCII, and an uppercase letter must occur after its first letter.
func ucElsewhere(word string) bool {
	rs := []rune(word)
	for i := 0; i <= len(rs); i++ {
		if i > 0 && !isPunct(rs[i-1]) {
			break
		}
		n := 0
		for i+n < len(rs) && isASCIILetter(rs[i+n]) {
			n++
		}
		if n >= 2 {
			for k := 1; k < n; k++ {
				if isASCIIUpper(rs[i+k]) {
					return true
				}
			}
		}
	}
	return false
}

func capFirst(word string) string {
	rs := []rune(word)
	for i, r := range rs {
		if isWord(r) {
			return pyUpper(string(rs[:i+1])) + string(rs[i+1:])
		}
		if !isPunct(r) {
			return word
		}
	}
	return word
}

func allConsonants(word string) bool {
	if word == "" {
		return false
	}
	for _, r := range word {
		if !isASCIIConsonant(r) {
			return false
		}
	}
	return true
}

func isASCIIConsonant(r rune) bool {
	if r >= 'A' && r <= 'Z' {
		r = r - 'A' + 'a'
	}
	if r < 'a' || r > 'z' {
		return false
	}
	switch r {
	case 'a', 'e', 'i', 'o', 'u', 'y':
		return false
	default:
		return true
	}
}

// Small-word alternatives in the order the Python expression tries them.
// "v." is tried before "v", and "vs." before "vs", because \.? is greedy.
var smallForms = []string{
	"a", "an", "and", "as", "at", "but", "by", "en", "for", "if", "in",
	"of", "on", "or", "the", "to", "v.", "v", "via", "vs.", "vs",
}

func smallWord(word string) bool {
	folded := foldASCII(word)
	for _, form := range []string{"a", "an", "and", "as", "at", "but", "by", "en", "for", "if", "in", "of", "on", "or", "the", "to", "v", "v.", "via", "vs", "vs."} {
		if folded == form {
			return true
		}
	}
	return false
}

// ^([punct]*)(small)\b  under re.I. punct* is greedy, then the first
// alternative that has a Python word boundary after it wins.
func applySmallFirst(word string) string {
	rs := []rune(word)
	maxPunct := 0
	for maxPunct < len(rs) && isPunct(rs[maxPunct]) {
		maxPunct++
	}
	for p := maxPunct; p >= 0; p-- {
		if n, ok := smallPrefix(rs[p:], true); ok {
			return string(rs[:p]) + pyCapitalize(string(rs[p:p+n])) + string(rs[p+n:])
		}
	}
	return word
}

// \b(small)[punct]?$ under re.I. The match has to reach the end, and the
// whole match, including one trailing punctuation character, is capitalized.
func applySmallLast(word string) string {
	rs := []rune(word)
	for i := 0; i <= len(rs); i++ {
		if !boundary(rs, i) {
			continue
		}
		if smallReachesEnd(rs[i:]) {
			return string(rs[:i]) + pyCapitalize(string(rs[i:]))
		}
	}
	return word
}

func smallPrefix(rs []rune, needBoundary bool) (int, bool) {
	for _, form := range smallForms {
		n := len(form) // ASCII
		if n > len(rs) || foldASCII(string(rs[:n])) != form {
			continue
		}
		if needBoundary && !boundary(rs, n) {
			continue
		}
		return n, true
	}
	return 0, false
}

func smallReachesEnd(rs []rune) bool {
	for _, form := range smallForms {
		n := len(form)
		if n > len(rs) || foldASCII(string(rs[:n])) != form {
			continue
		}
		rest := len(rs) - n
		if rest == 0 || (rest == 1 && isPunct(rs[n])) {
			return true
		}
	}
	return false
}

// ([:.;?!\-–‒—―][ ])(small) with no ignorecase flag and no word boundary.
// The first alternative wins, so "a" matches the first letter of "and".
func applySubphrase(line string) string {
	rs := []rune(line)
	var b strings.Builder
	for i := 0; i < len(rs); {
		if i+1 < len(rs) && isSubMark(rs[i]) && rs[i+1] == ' ' {
			if n, ok := exactSmallPrefix(rs[i+2:]); ok {
				b.WriteRune(rs[i])
				b.WriteRune(' ')
				b.WriteString(pyCapitalize(string(rs[i+2 : i+2+n])))
				i += 2 + n
				continue
			}
		}
		b.WriteRune(rs[i])
		i++
	}
	return b.String()
}

func exactSmallPrefix(rs []rune) (int, bool) {
	for _, form := range smallForms {
		if len(form) > len(rs) {
			continue
		}
		match := true
		for i := 0; i < len(form); i++ {
			if rs[i] != rune(form[i]) {
				match = false
				break
			}
		}
		if match {
			return len(form), true
		}
	}
	return 0, false
}

func isSubMark(r rune) bool {
	switch r {
	case ':', '.', ';', '?', '!', '-', '\u2012', '\u2013', '\u2014', '\u2015':
		return true
	default:
		return false
	}
}

func boundary(rs []rune, i int) bool {
	left := i > 0 && isWord(rs[i-1])
	right := i < len(rs) && isWord(rs[i])
	return left != right
}

func isWord(r rune) bool {
	return r == '_' || unicode.IsLetter(r) || unicode.Is(unicode.Number, r)
}

func isASCIILetter(r rune) bool {
	return (r >= 'A' && r <= 'Z') || (r >= 'a' && r <= 'z')
}

func isASCIIUpper(r rune) bool {
	return r >= 'A' && r <= 'Z'
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

func isPySpace(r rune) bool {
	switch r {
	case '\t', '\n', '\v', '\f', '\r', 0x1c, 0x1d, 0x1e, 0x1f, ' ',
		0x85, 0xa0, 0x1680, 0x2028, 0x2029, 0x202f, 0x205f, 0x3000:
		return true
	default:
		return r >= 0x2000 && r <= 0x200a
	}
}

// re.I for these ASCII patterns equates A-Z with a-z, I with İ/ı, and S with ſ.
func foldASCII(s string) string {
	rs := []rune(s)
	out := make([]rune, len(rs))
	for i, r := range rs {
		switch r {
		case 'I', 'İ', 'ı', 'i':
			out[i] = 'i'
		case 'S', 'ſ', 's':
			out[i] = 's'
		default:
			if r >= 'A' && r <= 'Z' {
				out[i] = r - 'A' + 'a'
			} else {
				out[i] = r
			}
		}
	}
	return string(out)
}

func pyCapitalize(s string) string {
	rs := []rune(s)
	if len(rs) == 0 {
		return ""
	}
	return pyUpper(string(rs[:1])) + pyLower(string(rs[1:]))
}

func pyLower(s string) string {
	var b strings.Builder
	for _, r := range s {
		if r == 'İ' {
			b.WriteString("i\u0307")
			continue
		}
		b.WriteRune(unicode.ToLower(r))
	}
	return b.String()
}

func pyUpper(s string) string {
	var b strings.Builder
	for _, r := range s {
		if exp, ok := upperExpand[r]; ok {
			b.WriteString(exp)
			continue
		}
		b.WriteRune(unicode.ToUpper(r))
	}
	return b.String()
}

// Characters whose Python str.upper() is more than one code point.
// Every other character uses Unicode simple uppercase.
var upperExpand = map[rune]string{
	0x00DF: "SS",
	0x0149: "\u02bcN",
	0x01F0: "J\u030c",
	0x0390: "\u0399\u0308\u0301",
	0x03B0: "\u03a5\u0308\u0301",
	0x0587: "\u0535\u0552",
	0x1E96: "H\u0331",
	0x1E97: "T\u0308",
	0x1E98: "W\u030a",
	0x1E99: "Y\u030a",
	0x1E9A: "A\u02be",
	0x1F50: "\u03a5\u0313",
	0x1F52: "\u03a5\u0313\u0300",
	0x1F54: "\u03a5\u0313\u0301",
	0x1F56: "\u03a5\u0313\u0342",
	0x1F80: "\u1f08\u0399",
	0x1F81: "\u1f09\u0399",
	0x1F82: "\u1f0a\u0399",
	0x1F83: "\u1f0b\u0399",
	0x1F84: "\u1f0c\u0399",
	0x1F85: "\u1f0d\u0399",
	0x1F86: "\u1f0e\u0399",
	0x1F87: "\u1f0f\u0399",
	0x1F88: "\u1f08\u0399",
	0x1F89: "\u1f09\u0399",
	0x1F8A: "\u1f0a\u0399",
	0x1F8B: "\u1f0b\u0399",
	0x1F8C: "\u1f0c\u0399",
	0x1F8D: "\u1f0d\u0399",
	0x1F8E: "\u1f0e\u0399",
	0x1F8F: "\u1f0f\u0399",
	0x1F90: "\u1f28\u0399",
	0x1F91: "\u1f29\u0399",
	0x1F92: "\u1f2a\u0399",
	0x1F93: "\u1f2b\u0399",
	0x1F94: "\u1f2c\u0399",
	0x1F95: "\u1f2d\u0399",
	0x1F96: "\u1f2e\u0399",
	0x1F97: "\u1f2f\u0399",
	0x1F98: "\u1f28\u0399",
	0x1F99: "\u1f29\u0399",
	0x1F9A: "\u1f2a\u0399",
	0x1F9B: "\u1f2b\u0399",
	0x1F9C: "\u1f2c\u0399",
	0x1F9D: "\u1f2d\u0399",
	0x1F9E: "\u1f2e\u0399",
	0x1F9F: "\u1f2f\u0399",
	0x1FA0: "\u1f68\u0399",
	0x1FA1: "\u1f69\u0399",
	0x1FA2: "\u1f6a\u0399",
	0x1FA3: "\u1f6b\u0399",
	0x1FA4: "\u1f6c\u0399",
	0x1FA5: "\u1f6d\u0399",
	0x1FA6: "\u1f6e\u0399",
	0x1FA7: "\u1f6f\u0399",
	0x1FA8: "\u1f68\u0399",
	0x1FA9: "\u1f69\u0399",
	0x1FAA: "\u1f6a\u0399",
	0x1FAB: "\u1f6b\u0399",
	0x1FAC: "\u1f6c\u0399",
	0x1FAD: "\u1f6d\u0399",
	0x1FAE: "\u1f6e\u0399",
	0x1FAF: "\u1f6f\u0399",
	0x1FB2: "\u1fba\u0399",
	0x1FB3: "\u0391\u0399",
	0x1FB4: "\u0386\u0399",
	0x1FB6: "\u0391\u0342",
	0x1FB7: "\u0391\u0342\u0399",
	0x1FBC: "\u0391\u0399",
	0x1FC2: "\u1fca\u0399",
	0x1FC3: "\u0397\u0399",
	0x1FC4: "\u0389\u0399",
	0x1FC6: "\u0397\u0342",
	0x1FC7: "\u0397\u0342\u0399",
	0x1FCC: "\u0397\u0399",
	0x1FD2: "\u0399\u0308\u0300",
	0x1FD3: "\u0399\u0308\u0301",
	0x1FD6: "\u0399\u0342",
	0x1FD7: "\u0399\u0308\u0342",
	0x1FE2: "\u03a5\u0308\u0300",
	0x1FE3: "\u03a5\u0308\u0301",
	0x1FE4: "\u03a1\u0313",
	0x1FE6: "\u03a5\u0342",
	0x1FE7: "\u03a5\u0308\u0342",
	0x1FF2: "\u1ffa\u0399",
	0x1FF3: "\u03a9\u0399",
	0x1FF4: "\u038f\u0399",
	0x1FF6: "\u03a9\u0342",
	0x1FF7: "\u03a9\u0342\u0399",
	0x1FFC: "\u03a9\u0399",
	0xFB00: "FF",
	0xFB01: "FI",
	0xFB02: "FL",
	0xFB03: "FFI",
	0xFB04: "FFL",
	0xFB05: "ST",
	0xFB06: "ST",
	0xFB13: "\u0544\u0546",
	0xFB14: "\u0544\u0535",
	0xFB15: "\u0544\u053b",
	0xFB16: "\u054e\u0546",
	0xFB17: "\u0544\u053d",
}
