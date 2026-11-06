#!/bin/bash
set -euo pipefail
cd /workspace/repo

cat > go.mod <<'EOF'
module titlecase

go 1.23
EOF

cat > main.go <<'EOF'
package main

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"strings"
	"unicode"
	"unicode/utf8"
)

const punctuation = "!\"“#$%&'‘()*+,-–‒—―./:;?@[\\]_`{|}~"

var smallWords = map[string]bool{
	"a": true, "an": true, "and": true, "as": true, "at": true,
	"but": true, "by": true, "en": true, "for": true, "if": true,
	"in": true, "of": true, "on": true, "or": true, "the": true,
	"to": true, "v": true, "v.": true, "via": true, "vs": true, "vs.": true,
}

func upperRune(r rune) string {
	// Python's full Unicode casing can expand a rune; preserve the common
	// expansions that Go's one-rune Unicode mapping cannot represent.
	switch r {
	case 'ß':
		return "SS"
	case 'ﬀ':
		return "FF"
	case 'ﬁ':
		return "FI"
	case 'ﬂ':
		return "FL"
	case 'ﬃ':
		return "FFI"
	case 'ﬄ':
		return "FFL"
	case 'ﬅ', 'ﬆ':
		return "ST"
	default:
		return string(unicode.ToUpper(r))
	}
}

func lowerRune(r rune) string {
	if r == 'İ' {
		return "i\u0307"
	}
	return string(unicode.ToLower(r))
}

func upper(s string) string {
	var b strings.Builder
	for _, r := range s {
		b.WriteString(upperRune(r))
	}
	return b.String()
}

func lower(s string) string {
	var b strings.Builder
	for _, r := range s {
		b.WriteString(lowerRune(r))
	}
	return b.String()
}

func capitalize(s string) string {
	if s == "" {
		return s
	}
	runes := []rune(s)
	var b strings.Builder
	b.WriteString(upperRune(runes[0]))
	for _, r := range runes[1:] {
		b.WriteString(lowerRune(r))
	}
	return b.String()
}

func isWordRune(r rune) bool {
	return unicode.IsLetter(r) || unicode.IsDigit(r) || r == '_'
}

func isPunctuation(r rune) bool {
	return strings.ContainsRune(punctuation, r)
}

func isSmall(s string) bool {
	return smallWords[lower(s)]
}

func isAllCaps(s string) bool {
	return upper(s) == s
}

func initials(s string) bool {
	runes := []rune(s)
	if len(runes) < 2 || len(runes)%2 != 0 {
		return false
	}
	for i := 0; i < len(runes); i += 2 {
		if !unicode.IsUpper(runes[i]) || runes[i+1] != '.' {
			return false
		}
	}
	return true
}

func letterPeriodLetter(s string) bool {
	runes := []rune(s)
	for i := 1; i+1 < len(runes); i++ {
		if unicode.IsLetter(runes[i-1]) && runes[i] == '.' && unicode.IsLetter(runes[i+1]) {
			return true
		}
	}
	return false
}

// Matches the useful behavior of the original leading-punctuation plus
// letters-with-an-uppercase-letter check without regexp lookarounds.
func hasInternalUpper(s string) bool {
	runes := []rune(s)
	i := 0
	for i < len(runes) && isPunctuation(runes[i]) {
		i++
	}
	letters := 0
	for ; i < len(runes) && unicode.IsLetter(runes[i]); i++ {
		if letters > 0 && unicode.IsUpper(runes[i]) {
			return true
		}
		letters++
	}
	return false
}

func apostropheSecond(s string) (int, []rune, bool) {
	r := []rune(s)
	if len(r) < 3 || !(unicode.ToLower(r[0]) == 'd' || unicode.ToLower(r[0]) == 'o' || unicode.ToLower(r[0]) == 'l') || (r[1] != '\'' && r[1] != '‘') {
		return 0, nil, false
	}
	end := len(r)
	if end >= 2 && isApostropheSuffix(r[end-2]) && isApostropheSuffix(r[end-1]) {
		end -= 2
	}
	if end < 3 {
		return 0, nil, false
	}
	for _, c := range r[2:end] {
		if !unicode.IsLetter(c) {
			return 0, nil, false
		}
	}
	return end, r, true
}

func isApostropheSuffix(r rune) bool { return r == '\'' || r == 's' }

func isMcPrefix(s string) (string, string, bool) {
	r := []rune(s)
	if len(r) < 4 || !(r[0] == 'm' || r[0] == 'M') || r[1] != 'c' && r[1] != 'C' {
		return "", "", false
	}
	if !isWordRune(r[2]) {
		return "", "", false
	}
	return string(r[:2]), string(r[2:]), true
}

func honorific(s string) bool {
	switch strings.ToLower(s) {
	case "mr", "mrs", "ms", "dr":
		return true
	}
	return false
}

func splitWhitespace(s string) ([]string, []string) {
	var words, spaces []string
	start := 0
	for i, r := range s {
		if unicode.IsSpace(r) {
			words = append(words, s[start:i])
			spaces = append(spaces, string(r))
			start = i + utf8.RuneLen(r)
		}
	}
	words = append(words, s[start:])
	return words, spaces
}

func titlecase(text string, smallFirstLast bool) string {
	// Python titlecase() splits on every CR/LF in preserve-blank-lines mode;
	// the stdin protocol gives us one line at a time, so process one logical
	// line here and preserve its other whitespace exactly.
	allCaps := isAllCaps(text)
	words, spaces := splitWhitespace(text)
	for i, word := range words {
		if allCaps && initials(word) {
			continue
		}
		if end, runes, ok := apostropheSecond(word); ok {
			first := runes[0]
			if unicode.ToLower(first) == 'd' || unicode.ToLower(first) == 'l' {
				first = unicode.ToLower(first)
			} else if unicode.ToLower(first) == 'o' {
				first = unicode.ToUpper(first)
			}
			runes[0] = first
			runes[2] = unicode.ToUpper(runes[2])
			words[i] = string(runes)
			_ = end
			continue
		}
		if _, rest, ok := isMcPrefix(word); ok {
			prefix, _, _ := isMcPrefix(word)
			words[i] = "Mc" + titlecase(rest, true)
			_ = prefix
			continue
		}
		if honorific(word) {
			r := []rune(word)
			r[0] = unicode.ToUpper(r[0])
			words[i] = string(r)
			continue
		}
		if letterPeriodLetter(word) || (!allCaps && hasInternalUpper(word)) {
			continue
		}
		if isSmall(word) {
			words[i] = lower(word)
			continue
		}
		if strings.Contains(word, "/") && !strings.Contains(word, "//") {
			parts := strings.Split(word, "/")
			for j := range parts {
				parts[j] = titlecase(parts[j], false)
			}
			words[i] = strings.Join(parts, "/")
			continue
		}
		if strings.Contains(word, "-") {
			parts := strings.Split(word, "-")
			for j := range parts {
				parts[j] = titlecase(parts[j], false)
			}
			words[i] = strings.Join(parts, "-")
			continue
		}
		if allCaps {
			word = lower(word)
		}
		if allConsonants(word) {
			words[i] = upper(word)
			continue
		}
		words[i] = capitalizeFirstAfterPunctuation(word)
	}

	if smallFirstLast && len(words) > 0 {
		words[0] = capSmallAtStart(words[0])
		words[len(words)-1] = capSmallAtEnd(words[len(words)-1])
	}

	var b strings.Builder
	for i, word := range words {
		if i > 0 && i-1 < len(spaces) {
			b.WriteString(spaces[i-1])
		}
		b.WriteString(word)
	}
	result := b.String()
	return capitalizeAfterSubphrase(result)
}

func allConsonants(s string) bool {
	r := []rune(s)
	if len(r) <= 2 {
		return false
	}
	for _, c := range r {
		lowerC := unicode.ToLower(c)
		if lowerC < 'a' || lowerC > 'z' || strings.ContainsRune("aeiouy", lowerC) {
			return false
		}
	}
	return true
}

func capitalizeFirstAfterPunctuation(s string) string {
	r := []rune(s)
	for i, c := range r {
		if unicode.IsLetter(c) {
			for _, before := range r[:i] {
				if !isPunctuation(before) {
					return s
				}
			}
			r[i] = unicode.ToUpper(c)
			return string(r)
		}
	}
	return s
}

func capSmallAtStart(s string) string {
	r := []rune(s)
	i := 0
	for i < len(r) && isPunctuation(r[i]) {
		i++
	}
	j := i
	for j < len(r) && isWordRune(r[j]) {
		j++
	}
	if i == j || !isSmall(string(r[i:j])) {
		return s
	}
	return string(r[:i]) + capitalize(string(r[i:j])) + string(r[j:])
}

func capSmallAtEnd(s string) string {
	r := []rune(s)
	end := len(r)
	if end > 0 && isPunctuation(r[end-1]) {
		end--
	}
	start := end
	for start > 0 && isWordRune(r[start-1]) {
		start--
	}
	if start == end || !isSmall(string(r[start:end])) {
		return s
	}
	return string(r[:start]) + capitalize(string(r[start:end])) + string(r[end:])
}

func capitalizeAfterSubphrase(s string) string {
	r := []rune(s)
	for i := 0; i+1 < len(r); i++ {
		if !strings.ContainsRune(":;.!?–‒—―", r[i]) || r[i+1] != ' ' {
			continue
		}
		start := i + 2
		end := start
		for end < len(r) && isWordRune(r[end]) {
			end++
		}
		if end > start && isSmall(string(r[start:end])) {
			cap := []rune(capitalize(string(r[start:end])))
			copy(r[start:end], cap)
		}
	}
	return string(r)
}

func processLine(line string) string {
	return titlecase(line, true)
}

func main() {
	reader := bufio.NewReader(os.Stdin)
	writer := bufio.NewWriter(os.Stdout)
	defer writer.Flush()
	for {
		line, err := reader.ReadString('\n')
		if len(line) > 0 {
			line = strings.TrimSuffix(line, "\n")
			line = strings.TrimSuffix(line, "\r")
			fmt.Fprintln(writer, processLine(line))
		}
		if err != nil {
			if err != io.EOF {
				fmt.Fprintln(os.Stderr, err)
				os.Exit(1)
			}
			break
		}
	}
}
EOF

find /workspace/repo -type f -name '*.py' -delete
rmdir /workspace/repo/titlecase
