from typing import List

class Solution:
    def maxDistance(self, arrays: List[List[int]]) -> int:
        res = 0
        length = len(arrays)
        max_val = arrays[0][-1]
        min_val = arrays[0][0]
        for i in range(1, length):
            res = max(res, arrays[i][-1] - min_val, max_val - arrays[i][0])
            min_val = min(min_val, arrays[i][0])
            max_val = max(max_val, arrays[i][-1])
        return res

if __name__ == "__main__":
    solution = Solution()
    print(solution.maxDistance([[1,2,3],[4,5],[1,2,3]]))
    print(solution.maxDistance([[1],[1]]))