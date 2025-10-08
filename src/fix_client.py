import argparse
import configparser
import quickfix as fix
import quickfix44 as fix44

ECHO_DEBUG = True

class Application(fix.Application):
    def __init__(self, username, password, symbols):
        super().__init__()
        self.username = username
        self.password = password
        self.symbols = symbols
        self.sessionID = None

    def onCreate(self, sessionID):
        # Session created
        pass

    def onLogon(self, sessionIDIn):
        self.sessionID = sessionIDIn
        print("✅ Logged on:", sessionIDIn)

        # Send a single MarketDataRequest for all symbols
        message = fix.Message()
        header = message.getHeader()
        header.setField(fix.MsgType("V"))  # MarketDataRequest

        # Required fields
        message.setField(fix.MDReqID("REQ-ALL"))
        message.setField(fix.SubscriptionRequestType("1"))  # Snapshot + Updates
        message.setField(fix.MarketDepth(1))
        message.setField(fix.NoMDEntryTypes(1))
        # MDEntryType group (bid)
        entry_group = fix.Group(267, 269)
        entry_group.setField(fix.MDEntryType('0'))  # '0' = Bid
        message.addGroup(entry_group)

        # Number of symbols
        message.setField(fix.NoRelatedSym(len(self.symbols)))
        # Add each symbol to the same request
        for symbol in self.symbols:
            sym_group = fix.Group(146, 55)
            sym_group.setField(fix.Symbol(symbol))
            message.addGroup(sym_group)

        fix.Session.sendToTarget(message, self.sessionID)
        print(f"📨 Sent MarketDataRequest for symbols: {self.symbols}")

    def onLogout(self, sessionID):
        print("🚪 Logged out:", sessionID)

    def toAdmin(self, message, sessionID):
        self.sessionID = sessionID
        msg_type = fix.MsgType()
        header = message.getHeader()
        header.getField(msg_type)
        if msg_type.getValue() == fix.MsgType_Logon:
            # Inject credentials on logon
            message.setField(fix.Username(self.username))
            message.setField(fix.Password(self.password))
            print(f"🔐 Sent credentials for user {self.username}")

    def fromAdmin(self, message, sessionID):
        print("⬅️ fromAdmin:", message.toString())

    def toApp(self, message, sessionID):
        print("📤 toApp:", message.toString())

    def fromApp(self, message, sessionID):
        print("📥 fromApp:", message.toString())
        try:
            symbol = message.getField(fix.Symbol().getField())
            print("📈 Received data for symbol:", symbol)
        except fix.FieldNotFound:
            pass

    def requestQuote(self):
        # Example: send a QuoteRequest
        print("🔁 Sending Quote Request")
        message = fix.Message()
        header = message.getHeader()
        header.setField(fix.MsgType("R"))  # QuoteRequest
        message.setField(fix.Symbol('CCCCCC'))
        fix.Session.sendToTarget(message, self.sessionID)


def main(config_file):
    print(f"📂 Loading config: {config_file}")
    try:
        # Parse credentials and symbols using configparser
        cfg = configparser.ConfigParser()
        cfg.read(config_file)
        section = cfg['DEFAULT'] if 'DEFAULT' in cfg else cfg[cfg.sections()[0]]
        username = section.get('Username')
        password = section.get('Password')
        symbols_str = section.get('Symbols', '')
        print(" Config ", username, password, symbols_str)
        
        # Support comma- or whitespace-separated symbols
        symbols = [sym.strip() for sym in symbols_str.replace(',', ' ').split() if sym.strip()]

        print(f"🔐 Credentials loaded: {username}/{'*' * len(password)}, Symbols: {symbols}")

        # Setup QuickFIX
        settings = fix.SessionSettings(config_file)
        application = Application(username, password, symbols)
        storeFactory = fix.FileStoreFactory(settings)
        logFactory = fix.FileLogFactory(settings)
        initiator = fix.SocketInitiator(application, storeFactory, settings, logFactory)

        initiator.start()
        print("🚀 FIX Initiator started. Type commands:")

        while True:
            cmd = input("Enter [q=quote, 2=exit, d=debug]: ").strip()
            if cmd == 'q':
                application.requestQuote()
            elif cmd == '2':
                print("👋 Exiting...")
                initiator.stop()
                break
            elif cmd == 'd':
                import pdb; pdb.set_trace()
            else:
                print("⚠️ Unknown command")

    except fix.ConfigError as e:
        print(f"❌ FIX ConfigError: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dynamic FIX Client')
    parser.add_argument('-c', '--configfile', default='clientLocal.cfg', help='Path to FIX config file')
    args = parser.parse_args()
    main(args.configfile)