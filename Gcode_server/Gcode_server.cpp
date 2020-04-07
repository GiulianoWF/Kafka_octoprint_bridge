#include <iostream>
#include <string>
#include <pistache/endpoint.h>

int main( int argc, char * argv[] ){
    std::cout << "Serving HTTP" << std::endl;

    struct ServeSkillHandler : public Pistache::Http::Handler {
        HTTP_PROTOTYPE(ServeSkillHandler)
        void onRequest(const Pistache::Http::Request& request, Pistache::Http::ResponseWriter response) override{
            auto resource       = request.resource();
            std::cout << "The resource is " << request.resource() <<  "\n";
            std::cout << "The client peer is: " << response.peer() <<std::endl;

            if (resource == "/get_gcode") {
                if (request.method() == Pistache::Http::Method::Get) {
                    auto part = std::string();
                    auto printer = std::string();

                    auto headers_list   = request.headers().rawList();
                    for (const auto & [HeaderKey, RawHeader] : headers_list) {
                        if      (HeaderKey == "printer") printer = RawHeader.value();
                        else if (HeaderKey == "part") part = RawHeader.value();

                        std::cout << HeaderKey << ": " << RawHeader.value() << std::endl;
                    }

                    auto path = "Gcodes/" + printer + "/" + part + ".gcode";
                    std::cout << "File to load: " << path << std::endl;

                    Pistache::Http::serveFile(response, path)
                        .then([](ssize_t bytes) {
                            std::cout << "Gcode sent whit size: " << bytes << " bytes" << std::endl;
                        }, Pistache::Async::NoExcept);
                }
            } else {
                response.send(Pistache::Http::Code::Not_Found);
            }
        }
    };

    auto endereco = Pistache::Address("*:9087");
    Pistache::Http::listenAndServe<ServeSkillHandler>(endereco);
}