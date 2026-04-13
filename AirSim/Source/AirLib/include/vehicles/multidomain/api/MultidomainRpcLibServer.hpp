#ifndef air_MultidomainRpcLibServer_hpp
#define air_MultidomainRpcLibServer_hpp

#include "common/Common.hpp"

#ifndef AIRLIB_NO_RPC

#include "api/RpcLibServerBase.hpp"

namespace msr {
    namespace airlib {

        class MultidomainRpcLibServer : public RpcLibServerBase
        {
        public:
            MultidomainRpcLibServer(ApiProvider* api_provider, string server_address, uint16_t port = RpcLibPort);
            virtual ~MultidomainRpcLibServer();
        };

    }
} //namespace msr::airlib

#endif // AIRLIB_NO_RPC

#endif // air_MultidomainRpcLibServer_hpp