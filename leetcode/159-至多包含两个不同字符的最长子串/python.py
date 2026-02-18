def length_of_longest_substring_two_distinct(s: str) -> int:
    # 或者手动检查 key 是否存在
    counter = {}
    left = 0
    res = 0

    for i, char in enumerate(s):
        counter[char] = counter.get(char, 0) + 1

        # 如果超过 2 种字符，移动左指针
        while len(counter) > 2:
            counter[s[left]] -= 1
            if counter[s[left]] == 0:
                del counter[s[left]]  # 删除计数为 0 的键
            left += 1

        res = max(res, i - left + 1)

    return res

if __name__ == "__main__":
    print(length_of_longest_substring_two_distinct("eceba"))
    print(length_of_longest_substring_two_distinct("ccaabbb"))