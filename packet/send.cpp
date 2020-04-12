#include <tins/tins.h>

#include <cassert>
#include <iostream>
#include <string>
#include <chrono>
#include <vector>
#include <algorithm>
#include <ctime>
#include <cstring>
#include <unordered_map>


#include <unistd.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <getopt.h>

using namespace Tins;


using payload_type = std::vector<uint8_t>;

static payload_type get_nowtime() {
    auto milliseconds_since_epoch =
    std::chrono::system_clock::now().time_since_epoch() / 
    std::chrono::microseconds(1);
    payload_type vec;
    while (milliseconds_since_epoch) {
        uint8_t t = milliseconds_since_epoch % 10;
        vec.push_back(t);
        milliseconds_since_epoch /= 10;
    }
    reverse(vec.begin(), vec.end());
    return vec;
}

static std::string get_randmac() {
    std::string mac;
    const static char sample[] = "0123456789abcdef";
    const int mod = strlen(sample);
    // #ifdef LOCAL
    //     std::cout << "mod = " << mod << std::endl;
    // #endif
    for (int i = 1; i <= 6; ++i) {
        mac.push_back(sample[rand() % mod]);
        mac.push_back(sample[rand() % mod]);
        if (i != 6) mac.push_back(':');
    }
    #ifdef LOCAL
        // std::cout << "rand mac: " << mac << std::endl;
    #endif
    return mac;
}


static std::string get_randip(const std::string RANDOM_IP_POOL = "10.0.10.222/8") {
    auto pos = RANDOM_IP_POOL.find('/');
    // std::cout << pos << std::endl;
    auto str_ip_addr = RANDOM_IP_POOL.substr(0, pos);
    auto str_ip_mask = RANDOM_IP_POOL.substr(pos + 1);
    // #ifdef LOCAL
    //     std::cout << "ip: " << str_ip_addr << std::endl;
    //     std::cout << "mask: " << str_ip_mask << std::endl;
    // #endif
    unsigned int mask = 0x0;
    for (int i = 31; i >= (31 - std::stoi(str_ip_mask)); --i) {
        mask |= (1 << i);
    }
    struct sockaddr_in adr_inet;
    if (inet_aton(str_ip_addr.c_str(), &adr_inet.sin_addr) != 1) {
        std::cerr << "inet_aton error" << std::endl;
        exit(1);
    }
    // std::cout << "????" << std::endl;
    unsigned int ip_addr = ntohl(adr_inet.sin_addr.s_addr);
    // std::cout << ip_addr << std::endl;
    // std::cout << htonl(ip_addr) << std::endl;
    // std::cout << ntohl(ip_addr) << std::endl;
    // #ifdef LCOAL
    //     std::cout << "32bit ip: " << ip_addr << std::endl;
    // #endif 
    // std::cout << "werwoei" << std::endl;
    unsigned int ip_addr_min = ip_addr & (mask & 0xffffffff);
    unsigned int ip_addr_max = ip_addr | (~mask & 0xffffffff);

    unsigned int dis = ip_addr_max - ip_addr_min;
    // std::cout << dis << std::endl;
    // std::srand(unsigned(time(NULL)));
    unsigned int ip_rand = ip_addr_min + (rand() % (dis == 0 ? 1 : dis));
    std::string str_ip_rand = std::string(inet_ntoa(in_addr{htonl(ip_rand)}));

    #ifdef LOCAL
        std::cout << "IP rand: " << str_ip_rand << std::endl;
    #endif
    return str_ip_rand;
}


static EthernetII getEthernetII(const std::string& dst_ip_ = "10.0.0.4", const std::string& dst_mac_ = "00:00:00:00:00:04",
            const std::string& src_ip_ = "10.0.0.1", const std::string& src_mac_ = "00:00:00:00:00:01",
            const int& sport_ = 12345, const int& dport_ = 12345) {
    return EthernetII(dst_mac_, src_mac_) /
        IP(dst_ip_, src_ip_) /
        UDP(dport_, sport_) / 
        RawPDU(get_nowtime());
}



int main(int argc, char **argv) {
    srand(unsigned(time(NULL)));
    std::string dest_ip = "10.0.0.4", dest_mac = "00:00:00:00:00:04";
    // 轮数
    int MAX_CNT = 1; //rand() % 10 + 1;
    int ch;
    while ((ch = getopt(argc, argv, "I:M:N:")) != -1) {
        switch (ch) {
            case 'I':
                dest_ip = std::string(optarg);
                break;
            case 'M':
                dest_mac = std::string(optarg);
                break;
            case 'N':
                MAX_CNT = atoi(optarg);                
                break;
        }
    }
    // std::cout << "dest_ip: " << dest_ip << "\n";
    // std::cout << "dest_mac: " << dest_mac << "\n";
    // std::cout << "MAX_CNT: " << MAX_CNT << "\n\n";




    auto interface_vec = NetworkInterface::all();
    NetworkInterface dev;
    bool flag = false;
    for (auto &ele : interface_vec) {
        if (!ele.is_loopback() && ele.is_up()) {
            dev = ele;
            flag = true;
            break;
        }
    }
    if (!flag) {
        std::cerr << "Can't find a interface.\n";
        exit(1);
    }


    #ifdef LOCAL
        NetworkInterface::Info info = dev.addresses();
        std::cout << "=====================================\n"
                  << "\tdevice name: " << dev.name() << "\n"
                  << "\tdevice ip:   " << info.ip_addr << "\n"
                  << "=====================================\n";

    #endif
    PacketSender sender;
    // auto eth = gen.getEthernetII();
    // sender.send(eth, iface);

    // const int MAX_CNT = (rand() % 10 + 2);
    // 每轮的发包数
    const int MAX_NUM = 70000;

    // const std::string dest_ip = "10.0.0.4";
    // const std::string dest_mac = "00:00:00:00:00:04";
    std::unordered_map<std::string, bool> vis;
    for (int packet_cnt = 0; packet_cnt < MAX_CNT; ++packet_cnt) {
        // std::cout << "\n";
    //    auto rand_ip = get_randip();
    //    if (vis.count(rand_ip)) continue;
        auto rand_ip = "10.0.0.1";
        auto rand_mac = get_randmac();
        // std::cout << rand_ip << "\n";
        for (int send_num = 0; send_num < MAX_NUM; ++send_num) {
            auto packet_to_send = getEthernetII(dest_ip, dest_mac, rand_ip, rand_mac);
            sender.send(packet_to_send, dev);
            // std::cout << "send packets\n";
            usleep(500);
            // usleep(800000);
            // sleep(1);
        }
    }

    return 0;
}
