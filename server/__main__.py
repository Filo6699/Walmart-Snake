from server.server import Server


if __name__ == "__main__":
    server = Server(("0.0.0.0", 12000))
    server.run()
