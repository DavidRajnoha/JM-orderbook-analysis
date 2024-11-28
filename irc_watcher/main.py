import irc.bot
import irc.strings
from irc.connection import Factory
import ssl

class LoggerBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        ssl_factory = Factory(wrapper=ssl.wrap_socket)
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, ssl_factory)], nickname, nickname)
        self.channel = channel

    def on_join(self, connection, event):
        if event.source.nick == self.connection.get_nickname():
            print(f"Successfully joined channel {self.channel}")

    def on_disconnect(self, connection, event):
        print("Disconnected from the server.")

    def on_welcome(self, connection, event):
        print("Connected to the server.")
        connection.join(self.channel)
        print(f"Joining channel {self.channel}")

    def on_pubmsg(self, connection, event):
        message = f"{event.source.nick}: {event.arguments[0]}"
        print(message)
        with open("chat.log", "a") as log_file:
            log_file.write(message + "\n")

if __name__ == "__main__":
    bot = LoggerBot("#joinmarket-pit", "DHE", "irc.cyberguerrilla.org")
    try:
        bot.start()
    except Exception as e:
        print(f"An error occurred: {e}")