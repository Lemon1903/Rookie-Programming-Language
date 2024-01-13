if __name__ == "__main__":
    with open("file1.rook", "r") as file:
        while True:
            line = file.readline()
            if not line:
                print("EOF")
                break
            print(line, end="")
