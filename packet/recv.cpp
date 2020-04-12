#include <tins/tins.h>

using namespace Tins;

#include <iostream>
#include <fstream>

static std::ofstream f{"record.log"};

class Consumer {
public:
    bool operator()(Packet& packet) {
        // std::cout << "pcaket.....\n";
        std::string ip_record = "";
        if (packet.pdu()->find_pdu<IP>()) {
            // std::cout << "At: " << packet.timestamp().microseconds()
                    //   << " - " << packet.pdu()->rfind_pdu<IP>().src_addr() << std::endl;
            ip_record = packet.pdu()->rfind_pdu<IP>().src_addr().to_string();
            // std::cout << "what happend " << ip_record << "\n";
        }

        if (packet.pdu()->find_pdu<RawPDU>()) {
            auto val = packet.pdu()->rfind_pdu<RawPDU>().payload();
            unsigned long pre = 0;
            for (const auto &ele : val) {
                pre = (pre * 10) + ele;
            }
            // std::cout << "pre: " << pre << std::endl;
            // std::cout << "timestamp: " << packet.timestamp().seconds() << " " << packet.timestamp().microseconds() << std::endl;
            auto test_now =
            std::chrono::system_clock::now().time_since_epoch() / 
            std::chrono::microseconds(1);
            // std::cout << "test_now: " << test_now << std::endl;
            // std::cout.flush();
            auto now = packet.timestamp().seconds() * 1000000 + packet.timestamp().microseconds();
            auto dif = (now - pre) / 1000.0;
            // std::cout << "now: " << now << " "
            std::cout << "dif: " << dif << " ms ";
            if (!ip_record.empty()) {
                // std::cout << "write to file" << "\n";
                std::cout << "ip： " << ip_record << "\n";
                std::cout.flush();
                // f << ip_record << " " << dif << "\n";
                // f.flush();
            }
        }
        return true;
    }
};



int main() {
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
        // std::cout << "=====================================\n"
        //           << "\tdevice name: " << dev.name() << "\n"
        //           << "\tdevice ip:   " << info.ip_addr << "\n"
        //           << "=====================================\n";

    #endif

    SnifferConfiguration config;
    config.set_filter("udp port 12345");
    config.set_promisc_mode(true);
    config.set_direction(PCAP_D_IN);
    config.set_timeout(1);
    config.set_snap_len(65535);
    config.set_immediate_mode(true);

    // std::cout << "press ctrl + c to exit" << "\n"
    //           << "\n----------------------\n"
    //           << "start sniffing....\n";
    Sniffer sniffer(dev.name(), config);

    sniffer.sniff_loop(Consumer(), 0);
}