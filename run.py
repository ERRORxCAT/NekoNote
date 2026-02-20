from core import App

def main():
    app = App()
    app._post_init()
    app.mainloop()

if __name__ == '__main__':
    main()