// Command titlecase is a byte-for-byte Go port of python-titlecase 2.4.1
// (the stdlib `re` code path). It reads one title per line on stdin and
// prints one titlecased result per line on stdout.
package main

import (
	"bufio"
	"fmt"
	"os"
	"regexp"
	"strings"
	"unicode"
)

const small = `a|an|and|as|at|but|by|en|for|if|in|of|on|or|the|to|v\.?|via|vs\.?`

// PUNCT from python-titlecase (same order and same runes).
const punct = `!"“#$%&'‘()*+,\-–‒—―./:;?@[\\\]_` + "`" + `{|}~`

var (
	smallWords = regexp.MustCompile(`(?i)^(` + small + `)$`)
	smallFirst = regexp.MustCompile(`(?i)^([` + punct + `]*)(` + small + `)\b`)
	smallLast  = regexp.MustCompile(`(?i)\b(` + small + `)([` + punct + `])?$`)
	subPhrase  = regexp.MustCompile(`([:.;?!\-–‒—―][ ])(` + small + `)`)
	mrMrsMsDr  = regexp.MustCompile(`(?i)^((m((rs?)|s))|Dr)$`)
	ucElsewhere = regexp.MustCompile(`^[` + punct + `]*?[a-zA-Z]+[A-Z]+?`)
	ucInitials  = regexp.MustCompile(`^(?:[A-Z]\.|[A-Z]\.[A-Z])+$`)
	allConsonant = regexp.MustCompile(`(?i)^[bcdfghjklmnpqrstvwxz]+$`)
)

func main() {
	in := bufio.NewScanner(os.Stdin)
	in.Buffer(make([]byte, 64*1024), 1024*1024)
	out := bufio.NewWriter(os.Stdout)
	defer out.Flush()
	for in.Scan() {
		fmt.Fprintln(out, titlecase(in.Text(), true))
	}
	if err := in.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

// titlecase mirrors titlecase.titlecase(text, callback=None,
// small_first_last=..., preserve_blank_lines=False,
// normalise_space_characters=False) for a single logical line.
func titlecase(text string, smallFirstLast bool) string {
	allCaps := strings.ToUpper(text) == text
	words, spaces := splitWords(text)

	processed := make([]string, len(words))
	for i, w := range words {
		processed[i] = titlecaseWord(w, allCaps)
	}

	if smallFirstLast && len(processed) > 0 {
		processed[0] = applySmallFirst(processed[0])
		processed[len(processed)-1] = applySmallLast(processed[len(processed)-1])
	}

	var b strings.Builder
	for i := range processed {
		b.WriteString(processed[i])
		if i < len(spaces) {
			b.WriteString(spaces[i])
		}
	}
	return subPhrase.ReplaceAllStringFunc(b.String(), func(m string) string {
		r := []rune(m)
		if len(r) < 3 {
			return m
		}
		return string(r[0]) + string(r[1]) + capitalize(string(r[2:]))
	})
}

func titlecaseWord(word string, allCaps bool) string {
	if allCaps && ucInitials.MatchString(word) {
		return word
	}

	if matchesAposSecond(word) {
		r := []rune(word)
		if len(r) >= 3 {
			if !isVowel(r[0]) {
				r[0] = unicode.ToLower(r[0])
			} else {
				r[0] = unicode.ToUpper(r[0])
			}
			r[2] = unicode.ToUpper(r[2])
		}
		return string(r)
	}

	if prefix, rest, ok := splitMacMc(word); ok {
		return capitalize(prefix) + titlecase(rest, true)
	}

	if mrMrsMsDr.MatchString(word) {
		r := []rune(word)
		if len(r) > 0 {
			r[0] = unicode.ToUpper(r[0])
		}
		return string(r)
	}

	if hasInlinePeriod(word) || (!allCaps && ucElsewhere.MatchString(word)) {
		return word
	}
	if smallWords.MatchString(word) {
		return strings.ToLower(word)
	}

	if strings.Contains(word, "/") && !strings.Contains(word, "//") {
		parts := strings.Split(word, "/")
		for i := range parts {
			parts[i] = titlecase(parts[i], false)
		}
		return strings.Join(parts, "/")
	}

	if strings.Contains(word, "-") {
		parts := strings.Split(word, "-")
		for i := range parts {
			parts[i] = titlecase(parts[i], false)
		}
		return strings.Join(parts, "-")
	}

	if allCaps {
		word = strings.ToLower(word)
	}

	if len([]rune(word)) > 2 && allConsonant.MatchString(word) {
		return strings.ToUpper(word)
	}

	return capFirst(word)
}

// splitWords reproduces re.split(r'(\s)', line): words at even indexes and
// the single whitespace characters between them at odd indexes.
func splitWords(line string) ([]string, []string) {
	var words, spaces []string
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

// matchesAposSecond is the stdlib-regex branch of APOS_SECOND:
// ^[dol]['‘][\w]+(?:['s]{2})?$  (Python \w is Unicode aware).
func matchesAposSecond(word string) bool {
	r := []rune(word)
	if len(r) < 3 || (r[0] != 'd' && r[0] != 'o' && r[0] != 'l' && r[0] != 'D' && r[0] != 'O' && r[0] != 'L') {
		return false
	}
	if r[1] != '\'' && r[1] != '‘' {
		return false
	}
	body := r[2:]
	if allWordRunes(body) {
		return true
	}
	if len(body) >= 3 {
		tail := body[len(body)-2:]
		if isAposOrS(tail[0]) && isAposOrS(tail[1]) && allWordRunes(body[:len(body)-2]) {
			return true
		}
	}
	return false
}

func isAposOrS(r rune) bool {
	return r == '\'' || r == 's' || r == 'S'
}

// splitMacMc is ^([Mm]c|MC)(\w.+).
func splitMacMc(word string) (string, string, bool) {
	r := []rune(word)
	if len(r) < 4 {
		return "", "", false
	}
	ok := (r[1] == 'c' && (r[0] == 'M' || r[0] == 'm')) || (r[0] == 'M' && r[1] == 'C')
	if !ok || !isWordRune(r[2]) {
		return "", "", false
	}
	return string(r[:2]), string(r[2:]), true
}

// hasInlinePeriod is the stdlib-regex branch of INLINE_PERIOD: [\w][.][\w].
func hasInlinePeriod(word string) bool {
	r := []rune(word)
	for i := 0; i+2 < len(r); i++ {
		if isWordRune(r[i]) && r[i+1] == '.' && isWordRune(r[i+2]) {
			return true
		}
	}
	return false
}

func isWordRune(r rune) bool {
	return r == '_' || unicode.IsLetter(r) || unicode.IsNumber(r)
}

var punctSet = func() map[rune]bool {
	m := map[rune]bool{}
	for _, r := range "!\"“#$%&'‘()*+,-–‒—―./:;?@[\\]_`{|}~" {
		m[r] = true
	}
	return m
}()

func isPunct(r rune) bool { return punctSet[r] }

func allWordRunes(r []rune) bool {
	if len(r) == 0 {
		return false
	}
	for _, c := range r {
		if !isWordRune(c) {
			return false
		}
	}
	return true
}

func applySmallFirst(word string) string {
	loc := smallFirst.FindStringSubmatchIndex(word)
	if loc == nil {
		return word
	}
	prefix := word[loc[2]:loc[3]]
	body := word[loc[4]:loc[5]]
	return prefix + capitalize(body) + word[loc[1]:]
}

func applySmallLast(word string) string {
	loc := smallLast.FindStringSubmatchIndex(word)
	if loc == nil {
		return word
	}
	return word[:loc[0]] + capitalize(word[loc[0]:loc[1]]) + word[loc[1]:]
}

// capFirst is CAPFIRST.sub(upper, word): ^[PUNCT]*?([\w]) with Python's
// Unicode-aware \w, uppercasing the whole match.
func capFirst(word string) string {
	r := []rune(word)
	for i, c := range r {
		if isWordRune(c) {
			r[i] = unicode.ToUpper(c)
			return string(r)
		}
		if !isPunct(c) {
			return word
		}
	}
	return word
}

// capitalize is Python str.capitalize: first rune upper, every other rune lower.
func capitalize(s string) string {
	r := []rune(s)
	if len(r) == 0 {
		return s
	}
	r[0] = unicode.ToUpper(r[0])
	for i := 1; i < len(r); i++ {
		r[i] = unicode.ToLower(r[i])
	}
	return string(r)
}

func isVowel(r rune) bool {
	switch r {
	case 'a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U':
		return true
	}
	return false
}
