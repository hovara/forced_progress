#include <cstring>
#include <iostream>

namespace interview {
void strcpy(char *dst, const char *src) {
  if (src == dst)
    return;

  int src_end = std::strlen(src);
  if (dst > src)
    for (int i = src_end; i >= 0; i--)
      *(dst + i) = *(src + i);
  else
    for (int i = 0; i <= src_end; i++)
      *(dst + i) = *(src + i);
}
} // namespace interview

int main() {
  char str[20] = "Hello world asdflk!";
  char dst[20];
  interview::strcpy(dst, str);
  interview::strcpy(str + 1, str);
  std::cout << dst << std::endl;
  std::cout << str;
}
