## TraderMade FIX 4.4 Market Data Integration Guide

This document provides an overview of the key FIX 4.4 message types supported by the TraderMade market data server. It is intended for client developers who need to integrate their FIX initiator with the TraderMade FIX acceptor.  

⚠️ **Note:** Only **market data** is supported. No order placement or trading is supported.

---

### Standard Header (all messages)

| Tag | Field         | Req | Description                                     |
|-----|---------------|-----|-------------------------------------------------|
| 8   | BeginString   | Y   | Protocol version (always FIX.4.4)               |
| 9   | BodyLength    | Y   | Length of message body                          |
| 35  | MsgType       | Y   | Identifies the message type                     |
| 49  | SenderCompID  | Y   | Assigned by TraderMade per client               |
| 56  | TargetCompID  | Y   | Always `TRADERMADE_M1` for this server          |
| 34  | MsgSeqNum     | Y   | Sequence number, increasing per session         |
| 52  | SendingTime   | Y   | UTC timestamp of sending                        |

---

### Standard Trailer

| Tag | Field     | Req | Description           |
|-----|-----------|-----|-----------------------|
| 10  | CheckSum  | Y   | 3-digit checksum      |

---

### Session (Admin) Messages

- **Logon (35=A)**  
  Client initiates session. Includes:  
  - `HeartBtInt (108)`  
  - `Username (553)`  
  - `Password (554)`

- **Heartbeat (35=0)**  
  Sent at fixed interval (30s default).

- **Test Request (35=1)**  
  Forces a heartbeat to verify connectivity.

- **Logout (35=5)**  
  Ends session gracefully.

- **Resend Request (35=2)**  
  Requests missing messages.

- **Reject (35=3) / Business Reject (35=j)**  
  Indicates error or unsupported message type.

- **Sequence Reset (35=4)**  
  Adjusts message sequence.

---

### Market Data Messages

- **Market Data Request (35=V)**  
  Used to subscribe/unsubscribe from symbols. Key fields:  
  - `MDReqID (262)` – unique request ID  
  - `SubscriptionRequestType (263)` – `1=Subscribe`, `2=Unsubscribe`  
  - `MarketDepth (264)` – depth (typically 1)  
  - `NoMDEntryTypes (267)` with `MDEntryType (269)` – `0=Bid`, `1=Offer`  
  - `NoRelatedSym (146)` with `Symbol (55)`  

- **Market Data Request Reject (35=Y)**  
  Returned if request cannot be fulfilled. Includes:  
  - `Reason code (281)`  
  - Optional `Text (58)`

- **Market Data Snapshot Full Refresh (35=W)**  
  Server delivers snapshot per symbol. Fields:  
  - `Symbol (55)`  
  - `MDReqID (262)`  
  - `NoMDEntries (268)`  
  - Repeated group with:  
    - `MDEntryType (269)`  
    - `MDEntryPx (270)`  
    - `MDEntrySize (271)`

---

### Example Encodings

#### Logon
```
8=FIX.4.4|35=A|34=1|49=CLIENT123|56=TRADERMADE_M1|98=0|108=30|553=<Username>|554=<Password>|10=063|
```

#### Market Data Request (subscribe GBPUSD)
```
8=FIX.4.4|35=V|49=CLIENT123|56=TRADERMADE_M1|34=2|52=20251002-09:30:00|262=REQ1|263=1|264=1|267=2|269=0|269=1|146=1|55=GBPUSD|10=210|
```

#### Market Data Request Reject
```
8=FIX.4.4|35=Y|49=TRADERMADE_M1|56=CLIENT123|34=3|52=20251002-09:30:01|262=REQ1|281=0|58=Unknown symbol|10=082|
```

#### Market Data Snapshot Full Refresh
```
8=FIX.4.4|35=W|49=TRADERMADE_M1|56=CLIENT123|34=4|52=20251002-09:30:01|55=GBPUSD|262=REQ1|268=2|269=0|270=1.2995|271=1000000|269=1|270=1.2997|271=1000000|10=128|
```

---

### Notes
- Only market data messages are supported by this server (**no order placement**).  
- Clients must manage sequence numbers and heartbeats as per FIX 4.4.  
- Use `ResetOnLogon=Y` and `ResetSeqNumFlag=Y` to simplify reconnects.  
- Subscription limits and symbol availability are enforced server-side; rejected requests will return `35=Y`.  
