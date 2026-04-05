#include <chrono>
#include <iostream>
#include <map>
#include <vector>

class Sender;
class Receiver;

class Receiver {
private:
  std::vector<int> received_messages;

public:
  void receive(int msg);
  void reply(Sender &A);
  void update(long long dt, Sender &A, long long delay);
};

class Sender {
private:
  std::map<int, int> M;

  bool COMM_ERR_FLAG = false;

public:
  void send_message(Receiver &r, int msg);
  void receive(int msg);
  void update(long long dt, Receiver &r, int &msg);
};

void Receiver::receive(int msg) {
  received_messages.insert(received_messages.begin(), msg);
}

void Receiver::reply(Sender &A) {
  int msg = received_messages.back();
  received_messages.pop_back();
  std::cout << "StationB replied with message: " << msg << std::endl;
  A.receive(msg);
}

void Receiver::update(long long dt, Sender &A, long long delay = 1000) {
  static long long elapsed = 0;
  elapsed += dt;
  if (elapsed >= delay) {
    elapsed -= delay;
    if (received_messages.size() > 0) {
      reply(A);
    }
  }
}

void Sender::send_message(Receiver &r, int msg) {
  M[msg] = 1000;
  // M[msg] = 5;
  /*inlocuind timpul de asteptare la 5 ms, in cazul acesta 5 update tickuri
   * permite depistarea (sau mai bine zis testarea comportamentului)
   * COMMUNICATIN ERR */
  r.receive(msg);
}

void Sender::receive(int msg) {
  try {
    if (M.at(msg) > 0) {
      std::cout << "StationA succesfully received back the message: " << msg
                << " with remaining time in ms: " << M.at(msg) << std::endl;
      M.erase(msg);
    } else
      throw 420;
  } catch (int flag) {
    M.erase(msg);
    COMM_ERR_FLAG = true;
  }
}

void Sender::update(long long dt, Receiver &r, int &msg) {
  static long long elapsed = 0;

  if (COMM_ERR_FLAG) {
    for (int i = 0; i < 3; i++)
      std::cout << "Communication error" << std::endl;
  }
  elapsed += dt;
  if (elapsed >= 1000) {
    elapsed -= 1000;
    // decrement timer on each sent message
    for (auto &[key, value] : M) {
      --value;
    }
    std::cout << "StationA sent message: " << msg << std::endl;
    send_message(r, msg++);
  }
}

long long get_elapsed_us() {
  static auto prev = std::chrono::steady_clock::now();
  auto curr = std::chrono::steady_clock::now();
  auto elapsed =
      std::chrono::duration_cast<std::chrono::microseconds>(curr - prev)
          .count();
  prev = curr;
  return elapsed;
}

int main() {
  Sender StationA;
  Receiver StationB;

  int msg = 1;

  while (msg < 10) {
    long long dt = get_elapsed_us();
    StationA.update(dt, StationB, msg);
    StationB.update(dt, StationA);
    // the delay controls the ration betwen sent:received_back messeages, i.e.
    // 3000 -> 3:1 StationB.update(dt, StationA, 3000);
    /* since I couldn't get the loop timing perfect, to simulate the
    COMMUNICATION error one would have to manually set the wait time for each
    sent message (inside Sender.send_message() to a arbitrarily low value i.e. 5
    in my commented line) */
  }

  return 0;
}
