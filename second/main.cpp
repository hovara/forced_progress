#include <iostream>
#include <string>
using namespace std;

int main() {
  string name;
  do {
    cout << "Enter your name: ";
    getline(cin, name);
  } while (name.empty()); // Keep asking until the user enters something (name
                          // is not empty)

  cout << "Hello, " << name;
  return 0;
}
