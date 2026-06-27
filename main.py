from commands.summarize import summarize

def main():
    summary = summarize("cronograma.csv")
    print(summary)

if __name__ == '__main__':
    main()


