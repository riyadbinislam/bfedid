import streamlit as st
import sqlite3
import hashlib
import simpy
from datetime import datetime

def setup_databases():
    conn_controller = sqlite3.connect('controller_node.db')
    c_controller = conn_controller.cursor()

    conn_blockchain = sqlite3.connect('blockchain.db')
    c_blockchain = conn_blockchain.cursor()

    c_blockchain.execute('''
        CREATE TABLE IF NOT EXISTS blocks (
            block_id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_hash TEXT,
            previous_hash TEXT,
            timestamp TEXT,
            transactions TEXT
        )
    ''')
    conn_blockchain.commit()
    return conn_controller, c_controller, conn_blockchain, c_blockchain

def controller_node(env, shareable_address, service, c_controller, transaction_queue):
    st.write(f"[{env.now}] Controller Node verifying {shareable_address}...")
    c_controller.execute('SELECT * FROM profiles WHERE shareable_address = ?', (shareable_address,))
    profile = c_controller.fetchone()

    if profile:
        name = profile[1]
        phone_number = profile[2]
        nonce = hashlib.sha256(f"{shareable_address}{service}{env.now}".encode()).hexdigest()

        transaction = {
            "shareable_address": shareable_address,
            "name": name,
            "phone_number": phone_number,
            "service": service,
            "nonce": nonce,
            "timestamp": datetime.now().isoformat(),
        }
        transaction_queue.append(transaction)
        st.success(f"Nonce generated and transaction verified for {name}.")
    else:
        st.error("Shareable address not found.")
    yield env.timeout(2)

def miner(env, transaction_queue, conn_blockchain, c_blockchain, blockchain):
    while True:
        if transaction_queue:
            st.write(f"[{env.now}] CN is verifying and mining transactions...")

            block = {
                "transactions": [],
                "timestamp": datetime.now().isoformat(),
                "previous_hash": blockchain[-1]["block_hash"] if blockchain else "0" * 64,
            }

            for _ in range(min(5, len(transaction_queue))):
                transaction = transaction_queue.pop(0)
                block["transactions"].append(transaction)

            block_data = str(block["transactions"]) + block["previous_hash"]
            block["block_hash"] = hashlib.sha256(block_data.encode()).hexdigest()
            blockchain.append(block)

            try:
                c_blockchain.execute('''
                    INSERT INTO blocks (block_hash, previous_hash, timestamp, transactions)
                    VALUES (?, ?, ?, ?)
                ''', (
                    block["block_hash"],
                    block["previous_hash"],
                    block["timestamp"],
                    str(block["transactions"])
                ))
                conn_blockchain.commit()

                c_blockchain.execute('SELECT * FROM blocks')
                blocks_debug = c_blockchain.fetchall()
                st.write("Blocks in Database After Save:", blocks_debug)

                st.success(f"Block saved with hash: {block['block_hash']}")
            except sqlite3.Error as e:
                st.error(f"Database Save Error: {e}")
                st.write("Block Data:", block)

        yield env.timeout(5)

def main():
    st.title("Service Request and Blockchain Management")

    conn_controller, c_controller, conn_blockchain, c_blockchain = setup_databases()

    if "transaction_queue" not in st.session_state:
        st.session_state.transaction_queue = []
    if "blockchain" not in st.session_state:
        st.session_state.blockchain = []

    page = st.sidebar.selectbox("Go to", ["Service Request", "Blockchain Viewer"])

    if page == "Service Request":
        shareable_address = st.text_input("Enter Shareable Address")
        service = st.selectbox("Select Service", ["Passport Renewal", "Scholarship Application", "Medical Record Access", "Background Check", "Electricity Bill Payment"])

        if st.button("Submit Request"):
            env = simpy.Environment()
            env.process(controller_node(env, shareable_address, service, c_controller, st.session_state.transaction_queue))
            env.run(until=2)

            st.write("Current Transaction Queue:", st.session_state.transaction_queue)

        if st.button("Start Mining"):
            st.write("Transaction Queue Before Mining:", st.session_state.transaction_queue)

            if not st.session_state.transaction_queue:
                st.error("No transactions in the queue. Cannot mine a block.")
            else:
                env = simpy.Environment()
                env.process(miner(env, st.session_state.transaction_queue, conn_blockchain, c_blockchain, st.session_state.blockchain))
                env.run(until=30)

                # Debug database state after mining
                c_blockchain.execute('SELECT * FROM blocks')
                blocks_debug = c_blockchain.fetchall()
                st.write("Blocks in Database After Mining:", blocks_debug)

                st.success("Mining process completed!")

    elif page == "Blockchain Viewer":
        st.header("Blockchain Viewer")

        try:
            c_blockchain.execute('SELECT * FROM blocks')
            blocks = c_blockchain.fetchall()

            st.write("Raw Blocks in Database in Viewer:", blocks)

            if blocks:
                for block in blocks:
                    st.subheader(f"Block ID: {block[0]}")
                    st.write(f"Hash: {block[1]}")
                    st.write(f"Previous Hash: {block[2]}")
                    st.write(f"Timestamp: {block[3]}")
                    st.write(f"Transactions: {block[4]}")
            else:
                st.write("No blocks mined yet.")
        except Exception as e:
            st.error(f"Error retrieving blocks from database: {e}")

if __name__ == "__main__":
    main()
