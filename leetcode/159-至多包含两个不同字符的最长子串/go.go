package main

import "fmt"

func lengthOfLongestSubstringTwoDistinct(s string) int {
	res := 0
	left := 0
	counter := make(map[byte]int) // 改为 map[byte]int

	for i := 0; i < len(s); i++ {
		// 增加当前字符的计数
		counter[s[i]]++

		// 如果超过 2 种字符，移动左指针
		for len(counter) > 2 {
			counter[s[left]]--
			if counter[s[left]] == 0 {
				delete(counter, s[left]) // 删除计数为 0 的键
			}
			left++
		}

		// 更新最大长度
		res = max(res, i+1-left) // 需要自己实现 max 函数
	}

	return res
}

// 辅助函数，计算两个整数的最大值
func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func main() {
	fmt.Println(lengthOfLongestSubstringTwoDistinct("eceba")) // 输出 3 ("ece")
	fmt.Println(lengthOfLongestSubstringTwoDistinct("ccaabbb")) // 输出 5 ("aabbb")
}