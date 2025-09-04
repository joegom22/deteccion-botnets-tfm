import os
import logging
import subprocess
import pandas as pd
import socket
import struct

logger = logging.getLogger("uvicorn")

OUTPUT_DIR = "/app/shared"

def int_to_ip(ip):
    """
    Convert an integer IP address to dotted notation.
    Args:
        ip (int or str): The integer or string representation of the IP address.
    """
    try:
        ip = socket.inet_ntoa(struct.pack("!I", int(ip)))
        return ip
    except:
        return ip

def create_flows(pcap_file):
    """
    Create traffic flows from the gathered PCAP file using cicflowmeter.

    Args:
        pcap_file (str): Path to the PCAP file to process.
        
    Returns:
        str: Path to the generated CSV file containing traffic flows.
    """
    try:
        subprocess.run([
            "tshark", "-r", pcap_file,
            "-T", "fields",
            "-E", "separator=,",
            "-e", "frame.time_epoch",
            "-e", "ip.src",
            "-e", "ip.dst",
            "-e", "tcp.srcport",
            "-e", "tcp.dstport",
            "-e", "udp.srcport",
            "-e", "udp.dstport",
            "-e", "ip.proto",
            "-e", "frame.len",
            "-Y", "ip"
        ], stdout=open(os.path.join(OUTPUT_DIR, "flows_raw.csv"), "w"))
        return os.path.join(OUTPUT_DIR, "flows_raw.csv")
    
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to create traffic flows: {e}")

def process_tshark_output(tshark_output):
    """
    Process the output from tshark to extract flow information.
    
    Args:
        tshark_output (str): The output from the tshark command.
        
    Returns:
        list: A list of dictionaries containing the extracted information.
    """
    df = pd.read_csv(
        tshark_output,
        names=["timestamp", "src_ip", "dst_ip", "tcp_srcport", "tcp_dstport", "udp_srcport", "udp_dstport", "protocol", "bytes"],
        header=None,
        on_bad_lines='skip'
    )

    logger.info("Processing tshark output...")
    df["src_port"] = df["tcp_srcport"].fillna(df["udp_srcport"])
    df["dst_port"] = df["tcp_dstport"].fillna(df["udp_dstport"])
    df.drop(columns=["tcp_srcport", "tcp_dstport", "udp_srcport", "udp_dstport"], inplace=True)

    # Tshark protocol mapping from integer to string
    protocol_mapping = {
        1: "ICMP",
        2: "IGMP",
        6: "TCP",
        17: "UDP",
        41: "IPv6",
        47: "GRE",
        50: "ESP",
        51: "AH",
        58: "IPv6-ICMP",
        88: "EIGRP",
        89: "OSPFIGP",
        132: "SCTP",
        137: "MPLS-in-IP"
    }

    # Convert protocol numbers to strings
    df['protocol'] = df['protocol'].apply(lambda x: protocol_mapping.get(int(x), f"Unknown Protocol Codification: {x}"))
    
    # Convert int ips to dotted notation
    df['src_ip'] = df['src_ip'].apply(int_to_ip)
    df['dst_ip'] = df['dst_ip'].apply(int_to_ip)

    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    logger.info("Converted timestamps and IPs to human-readable format.")

    # We want to get the flows from every pair of source and destination IPs and ports, with the protocol and bytes transferred as well as the flow duration.
    logger.info("Grouping conversations by source, destination, and protocol...")
    grouped_dfs = {}

    for group_key, group_df in df.groupby(['src_ip', 'dst_ip', 'src_port', 'dst_port', 'protocol']):
        group_df_sorted = group_df.sort_values(by=['timestamp']).reset_index(drop=True)

        grouped_dfs[group_key] = group_df_sorted
    logger.info(f"Grouped conversations into {len(grouped_dfs)} unique pairs of source and destination IPs.")
    grouped_dfs = {k: v for k, v in grouped_dfs.items() if len(v) > 1}

    timestamp_col = 'timestamp'
    time_threshold = 30
    total_flows = []
    flows_summary = []
    for (src, dst, src_port, dst_port, proto), group_df in grouped_dfs.items():
        flows = []
        segment = [group_df.iloc[0]]
        for i in range(1, len(group_df)):
            current_time = group_df.iloc[i][timestamp_col]
            previous_time = group_df.iloc[i - 1][timestamp_col]
            
            if (current_time - previous_time).total_seconds() > time_threshold:
                segment_df = pd.DataFrame(segment)
                flows.append(segment_df)
            else:
                segment.append(group_df.iloc[i])
                        
        if segment:
            flows.append(pd.DataFrame(segment))
        
        total_flows.append({"Flows": flows})
    
        for flow in flows:
            flow = flow.copy()
            flows_summary.append({
                "src_ip": src,
                "dst_ip": dst,
                "src_port": src_port,
                "dst_port": dst_port,
                "protocol": proto,
                "num_packets_src": (flow["src_ip"] == src).sum(),
                "num_packets_dst": (flow["dst_ip"] == dst).sum(),
                "bytes_src": flow.loc[flow["src_ip"] == src, "bytes"].sum(),
                "bytes_dst": flow.loc[flow["dst_ip"] == dst, "bytes"].sum(),
                "duration": (flow["timestamp"].max() - flow["timestamp"].min()).total_seconds()
            })
    
    logger.info(f"Processed {len(total_flows)} flows with {len(flows_summary)} summary entries.")
    
    df = pd.DataFrame(flows_summary)
    logger.info("Converted flows summary to DataFrame.")
    df.to_csv(os.path.join(OUTPUT_DIR, "flows_summary.csv"), index=False)
    logger.info("Saved flows summary to CSV.")
    return os.path.join(OUTPUT_DIR, "flows_summary.csv")