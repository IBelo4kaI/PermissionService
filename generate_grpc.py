from grpc_tools import protoc

protoc.main(
    (
        "",
        "-I./proto",
        "--python_out=./generated",
        "--grpc_python_out=./generated",
        "--pyi_out=./generated",
        "./proto/permission.proto",
    )
)
