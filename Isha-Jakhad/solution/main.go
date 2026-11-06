package main

import (
	"bufio"
	"fmt"
	"os"
)

func main() {
	in := bufio.NewScanner(os.Stdin)
	in.Buffer(make([]byte, 64*1024), 32*1024*1024)
	for in.Scan() {
		fmt.Println(processLine(in.Text(), true))
	}
}
