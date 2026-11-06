#!/bin/bash
set -euo pipefail

repo=/workspace/repo
mkdir -p "$repo"

cat > "$repo/go.mod" <<'EOF'
module titlecase

go 1.23
EOF

cat > "$repo/main.go" <<'EOF'
package main

import (
	"bufio"
	"os"
	"regexp"
	"strings"
	"unicode"
	"unicode/utf8"
)

const punctSet = "!\"“#$%&'‘()*+,-–‒—―./:;?@[\\]_`{|}~"

var subphrase = regexp.MustCompile(`([:.;?!` + "\u2013\u2012\u2014\u2015" + `-] )(a|an|and|as|at|but|by|en|for|if|in|of|on|or|the|to|v\.?|via|vs\.?)`)

func isPunct(r rune) bool {
	return strings.ContainsRune(punctSet, r)
}

func isWord(r rune) bool {
	return r == '_' || unicode.IsLetter(r) || unicode.IsDigit(r)
}

func isPySpace(r rune) bool {
	return unicode.IsSpace(r)
}

func boundaryAt(rs []rune, pos int) bool {
	left := pos > 0 && isWord(rs[pos-1])
	right := pos < len(rs) && isWord(rs[pos])
	return left != right
}

func capitalize(s string) string {
	if s == "" {
		return s
	}
	r, size := utf8.DecodeRuneInString(s)
	return string(unicode.ToUpper(r)) + strings.ToLower(s[size:])
}

func pyUpper(s string) string {
	return strings.ToUpper(s)
}

func pyLower(s string) string {
	return strings.ToLower(s)
}

func splitWS(s string) (words, spaces []string) {
	var word strings.Builder
	atWord := true
	for _, r := range s {
		if isPySpace(r) {
			if atWord {
				words = append(words, word.String())
				word.Reset()
				atWord = false
			}
			spaces = append(spaces, string(r))
			continue
		}
		atWord = true
		word.WriteRune(r)
	}
	if atWord {
		words = append(words, word.String())
	}
	return words, spaces
}

func joinWords(words, spaces []string) string {
	out := make([]string, len(words)+len(spaces))
	for i := range words {
		out[i*2] = words[i]
	}
	for i := range spaces {
		out[i*2+1] = spaces[i]
	}
	return strings.Join(out, "")
}

func isSmallWord(word string) bool {
	switch pyLower(word) {
	case "a", "an", "and", "as", "at", "but", "by", "en", "for", "if", "in", "of", "on", "or", "the", "to", "via", "v", "v.", "vs", "vs.":
		return true
	default:
		return false
	}
}

func isHonorific(word string) bool {
	switch pyLower(word) {
	case "mr", "mrs", "ms", "dr":
		return true
	default:
		return false
	}
}

func isAZ(r rune) bool {
	return r >= 'A' && r <= 'Z'
}

func isInitials(word string) bool {
	rs := []rune(word)
	if len(rs) == 0 {
		return false
	}
	i := 0
	for i < len(rs) {
		if i+2 < len(rs) && isAZ(rs[i]) && rs[i+1] == '.' && isAZ(rs[i+2]) && (i+3 == len(rs) || rs[i+3] != '.') {
			// Prefer [A-Z]\. when the following dot form also fits by backtracking.
			if i+3 == len(rs) {
				i += 3
				continue
			}
		}
		if i+1 < len(rs) && isAZ(rs[i]) && rs[i+1] == '.' {
			i += 2
			continue
		}
		if i+2 < len(rs) && isAZ(rs[i]) && rs[i+1] == '.' && isAZ(rs[i+2]) {
			i += 3
			continue
		}
		return false
	}
	return true
}

func hasInlinePeriod(word string) bool {
	rs := []rune(word)
	for i := 0; i+2 < len(rs); i++ {
		if isWord(rs[i]) && rs[i+1] == '.' && isWord(rs[i+2]) {
			return true
		}
	}
	return false
}

func hasUpperElsewhere(word string) bool {
	rs := []rune(word)
	i := 0
	for i < len(rs) && isPunct(rs[i]) {
		i++
	}
	start := i
	for i < len(rs) && ((rs[i] >= 'A' && rs[i] <= 'Z') || (rs[i] >= 'a' && rs[i] <= 'z')) {
		i++
	}
	run := rs[start:i]
	if len(run) < 2 {
		return false
	}
	for _, r := range run[1:] {
		if r >= 'A' && r <= 'Z' {
			return true
		}
	}
	return false
}

func capfirst(word string) string {
	rs := []rune(word)
	i := 0
	for i < len(rs) && isPunct(rs[i]) {
		i++
	}
	if i >= len(rs) || !isWord(rs[i]) {
		return word
	}
	head := string(rs[:i+1])
	return pyUpper(head) + string(rs[i+1:])
}

func allConsonants(word string) bool {
	n := utf8.RuneCountInString(word)
	if n <= 2 {
		return false
	}
	for _, r := range word {
		if r >= 'A' && r <= 'Z' {
			r = r - 'A' + 'a'
		}
		if !strings.ContainsRune("bcdfghjklmnpqrstvwxz", r) {
			return false
		}
	}
	return true
}

func matchApos(word string) bool {
	rs := []rune(word)
	if len(rs) < 3 {
		return false
	}
	switch unicode.ToLower(rs[0]) {
	case 'd', 'o', 'l':
	default:
		return false
	}
	if rs[1] != '\'' && rs[1] != '‘' {
		return false
	}
	i := 2
	if !isWord(rs[i]) {
		return false
	}
	i++
	for i < len(rs) && isWord(rs[i]) {
		i++
	}
	if i == len(rs) {
		return true
	}
	if len(rs)-i == 2 && isAposTail(rs[i]) && isAposTail(rs[i+1]) {
		return true
	}
	// \w+ may back off by two characters when those are also word characters.
	if i >= 2 && len(rs)-i == 0 {
		return true
	}
	if len(rs) >= 4 && isWord(rs[2]) {
		j := len(rs) - 2
		if j > 2 && isAposTail(rs[j]) && isAposTail(rs[j+1]) {
			allWord := true
			for k := 2; k < j; k++ {
				if !isWord(rs[k]) {
					allWord = false
					break
				}
			}
			if allWord {
				return true
			}
		}
	}
	return false
}

func isAposTail(r rune) bool {
	return r == '\'' || r == 's' || r == 'S'
}

func fixApos(word string) string {
	rs := []rune(word)
	if !strings.ContainsRune("aeiouAEIOU", rs[0]) {
		rs[0] = unicode.ToLower(rs[0])
	} else {
		rs[0] = unicode.ToUpper(rs[0])
	}
	rs[2] = unicode.ToUpper(rs[2])
	return string(rs)
}

func macPrefix(word string) (string, string, bool) {
	rs := []rune(word)
	if len(rs) < 4 {
		return "", "", false
	}
	var prefix int
	if (rs[0] == 'M' || rs[0] == 'm') && rs[1] == 'c' {
		prefix = 2
	} else if rs[0] == 'M' && rs[1] == 'C' {
		prefix = 2
	} else {
		return "", "", false
	}
	if !isWord(rs[prefix]) || len(rs)-prefix < 2 {
		return "", "", false
	}
	return string(rs[:prefix]), string(rs[prefix:]), true
}

func applySubphrase(s string) string {
	return subphrase.ReplaceAllStringFunc(s, func(match string) string {
		parts := subphrase.FindStringSubmatch(match)
		if len(parts) != 3 {
			return match
		}
		return parts[1] + capitalize(parts[2])
	})
}

func matchSmallPrefix(rs []rune, i int, ignoreCase bool) int {
	try := func(lit string) int {
		l := []rune(lit)
		if i+len(l) > len(rs) {
			return -1
		}
		for k, want := range l {
			got := rs[i+k]
			if ignoreCase {
				if unicode.ToLower(got) != unicode.ToLower(want) {
					return -1
				}
			} else if got != want {
				return -1
			}
		}
		return len(l)
	}
	consider := func(lit string) int {
		n := try(lit)
		if n < 0 || !boundaryAt(rs, i+n) {
			return -1
		}
		return n
	}
	for _, lit := range []string{"a", "an", "and", "as", "at", "but", "by", "en", "for", "if", "in", "of", "on", "or", "the", "to"} {
		if n := consider(lit); n >= 0 {
			return n
		}
	}
	if n := consider("v."); n >= 0 {
		return n
	}
	if n := consider("v"); n >= 0 {
		return n
	}
	if n := consider("via"); n >= 0 {
		return n
	}
	if n := consider("vs."); n >= 0 {
		return n
	}
	if n := consider("vs"); n >= 0 {
		return n
	}
	return -1
}

func applySmallFirst(word string) string {
	rs := []rune(word)
	i := 0
	for i < len(rs) && isPunct(rs[i]) {
		i++
	}
	n := matchSmallPrefix(rs, i, true)
	if n < 0 {
		return word
	}
	small := string(rs[i : i+n])
	return string(rs[:i]) + capitalize(small) + string(rs[i+n:])
}

func applySmallLast(word string) string {
	rs := []rune(word)
	try := func(punct int) (string, bool) {
		end := len(rs) - punct
		if end < 0 {
			return "", false
		}
		for _, lit := range []string{"a", "an", "and", "as", "at", "but", "by", "en", "for", "if", "in", "of", "on", "or", "the", "to", "v.", "v", "via", "vs.", "vs"} {
			l := []rune(lit)
			start := end - len(l)
			if start < 0 {
				continue
			}
			ok := true
			for k, want := range l {
				if unicode.ToLower(rs[start+k]) != unicode.ToLower(want) {
					ok = false
					break
				}
			}
			if !ok || !boundaryAt(rs, start) {
				continue
			}
			matched := string(rs[start:])
			return string(rs[:start]) + capitalize(matched), true
		}
		return "", false
	}
	if len(rs) > 0 && isPunct(rs[len(rs)-1]) {
		if s, ok := try(1); ok {
			return s
		}
	}
	if s, ok := try(0); ok {
		return s
	}
	return word
}

func titlecase(text string, smallFirstLast bool) string {
	lines := splitLines(text, false)
	processed := make([]string, 0, len(lines))
	for _, line := range lines {
		allCaps := pyUpper(line) == line
		words, spaces := splitWS(line)
		tc := make([]string, 0, len(words))
		for _, word := range words {
			if allCaps && isInitials(word) {
				tc = append(tc, word)
				continue
			}
			if matchApos(word) {
				tc = append(tc, fixApos(word))
				continue
			}
			if prefix, rest, ok := macPrefix(word); ok {
				tc = append(tc, capitalize(prefix)+titlecase(rest, true))
				continue
			}
			if isHonorific(word) {
				rs := []rune(word)
				rs[0] = unicode.ToUpper(rs[0])
				tc = append(tc, string(rs))
				continue
			}
			if hasInlinePeriod(word) || (!allCaps && hasUpperElsewhere(word)) {
				tc = append(tc, word)
				continue
			}
			if isSmallWord(word) {
				tc = append(tc, pyLower(word))
				continue
			}
			if strings.Contains(word, "/") && !strings.Contains(word, "//") {
				parts := strings.Split(word, "/")
				for i, part := range parts {
					parts[i] = titlecase(part, false)
				}
				tc = append(tc, strings.Join(parts, "/"))
				continue
			}
			if strings.Contains(word, "-") {
				parts := strings.Split(word, "-")
				for i, part := range parts {
					parts[i] = titlecase(part, false)
				}
				tc = append(tc, strings.Join(parts, "-"))
				continue
			}
			if allCaps {
				word = pyLower(word)
			}
			if allConsonants(word) {
				tc = append(tc, pyUpper(word))
				continue
			}
			tc = append(tc, capfirst(word))
		}
		if smallFirstLast && len(tc) > 0 {
			tc[0] = applySmallFirst(tc[0])
			tc[len(tc)-1] = applySmallLast(tc[len(tc)-1])
		}
		processed = append(processed, applySubphrase(joinWords(tc, spaces)))
	}
	return strings.Join(processed, "\n")
}

func splitLines(text string, preserve bool) []string {
	if text == "" {
		return []string{""}
	}
	if preserve {
		return strings.FieldsFunc(text, func(r rune) bool { return r == '\n' || r == '\r' })
	}
	parts := strings.FieldsFunc(text, func(r rune) bool { return r == '\n' || r == '\r' })
	if len(parts) == 0 {
		return []string{""}
	}
	return parts
}

func main() {
	in := bufio.NewScanner(os.Stdin)
	in.Buffer(make([]byte, 0, 64*1024), 10*1024*1024)
	out := bufio.NewWriter(os.Stdout)
	for in.Scan() {
		out.WriteString(titlecase(in.Text(), true))
		out.WriteByte('\n')
	}
	out.Flush()
}
EOF

find "$repo" -type f -name '*.py' -delete
# go build writes the binary named after the module, "titlecase".
# The leftover Python package directory would make that build fail.
rm -rf "$repo/titlecase"
