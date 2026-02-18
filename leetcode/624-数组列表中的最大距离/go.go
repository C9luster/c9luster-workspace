package main

import "fmt"

func max(a, b int) int {
    if a > b {
        return a
    }
    return b
}

func min(a, b int) int {
    if a < b {
        return a
    }
    return b
}

func maxDistance(arrays [][]int) int {
    res := 0
    n := len(arrays[0])
    minVar := arrays[0][0]
    maxVar := arrays[0][n - 1]
    for i:= 1; i < len(arrays); i++ {
        n = len(arrays[i])
        res = max(res, max(maxVar - arrays[i][0], arrays[i][n - 1] - minVar))
        maxVar = max(maxVar, arrays[i][n - 1])
        minVar = min(minVar, arrays[i][0])
    }
    return res
}

func main() {
    // 测试用例 1: [[1,2,3],[4,5],[1,2,3]]
    arrays1 := [][]int{{1, 2, 3}, {4, 5}, {1, 2, 3}}
    fmt.Println(maxDistance(arrays1))
    
    // 测试用例 2: [[1],[1]]
    arrays2 := [][]int{{1}, {1}}
    fmt.Println(maxDistance(arrays2))
}