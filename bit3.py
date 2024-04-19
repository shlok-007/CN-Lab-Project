import random
import numpy as np 
import matplotlib.pyplot as plt

#upload bandwidth greedily divided based on number of pieces received by the peers and reciprocation allowed

file_len = 50
num_peers = 100

class Peer:
    def __init__(self, id, is_seeder=False):
        self.id = id
        self.is_seeder = is_seeder
        self.pieces = set()
        self.upload_rate_mean = int(np.random.uniform(100.0, 800.0))
        self.upload_rate = self.upload_rate_mean  # Simulated capability
        self.upload_bandwidth = self.upload_rate // 100  # Max pieces per step
        self.max_download_bandwidth = 8  # Max pieces to download per step
        if is_seeder:
            self.pieces = set(range(file_len))  # Seeder starts with all pieces
        self.download_count_last_step = 0
        self.downloaded_pieces = 0
        self.upload_count_last_step = 0
        self.uploaded_pieces = 0
        self.completed_step = 0
        self.unchoked_by = set()

    def adjust_upload_rate(self):
        self.upload_rate = max(int(random.normalvariate(self.upload_rate_mean, 80)), 100)
        self.upload_bandwidth = self.upload_rate // 100

    def reset_bandwidth_usage(self):
        self.download_count_last_step = 0
        self.upload_count_last_step = 0
        self.unchoked_by.clear()

    def __str__(self):
        completion_info = f", Completed at Step: {self.completed_step}" if self.is_seeder else ""
        return (f"Peer {self.id}: Pieces={len(self.pieces)}, Seeder={self.is_seeder}, "
                f"Upload Rate={self.upload_rate}, Max Upload BW={self.upload_bandwidth}, "
                f"Max Download BW={self.max_download_bandwidth}, "
                f"Recent Uploads={self.upload_count_last_step}, Recent Downloads={self.download_count_last_step}{completion_info}")

class TorrentNetwork:
    def __init__(self):
        self.peers = [Peer(id=1, is_seeder=True)]  # Seeder
        self.peers.extend(Peer(id=i+2) for i in range(num_peers))  # Leechers
        self.piece_freq = [1]*file_len

    def all_have_files(self):
        return all(peer.is_seeder for peer in self.peers)

    def perform_choke_unchoke(self, current_step):
        # Reset all peers' bandwidth usage and unchoked_by list before making new decisions
        for peer in self.peers:
            peer.reset_bandwidth_usage()

        unchoking_decisions = {}
        for peer in self.peers:
            if peer.is_seeder:
                eligible_peers = [p for p in self.peers if p.id != peer.id and not p.is_seeder and len(p.pieces) < file_len]
            else:
                eligible_peers = [p for p in self.peers if p.id != peer.id and not p.is_seeder and list((p.pieces) -(peer.pieces))]

            eligible_peers.sort(key=lambda x: (-len(x.pieces)), reverse=True)
            top_peers = eligible_peers[:3]  # Select top 3 peers based on priority
            if current_step % 3 == 0 and eligible_peers:
                optimistic_peer = random.choice(eligible_peers)
                top_peers.append(optimistic_peer)

            unchoking_decisions[peer] = top_peers
            for chosen_peer in top_peers:
                chosen_peer.unchoked_by.add(peer.id)
                if not peer.is_seeder:
                    peer.unchoked_by.add(chosen_peer.id)

        # Share pieces based on unchoking decisions
        for peer, top_peers in unchoking_decisions.items():
            self.share_pieces(peer, top_peers,current_step)

    def share_pieces(self, peer, top_peers,current_step):
        n_chosen = len(top_peers)
        top_peers.sort(key=lambda x: -len(x.pieces), reverse=True)
        for chosen_peer in top_peers:
            if peer.upload_count_last_step < peer.upload_bandwidth:
                available_pieces = list(peer.pieces - chosen_peer.pieces)
                available_pieces.sort(key=lambda x: self.piece_freq[x])
                pieces_to_transfer = min(len(available_pieces), chosen_peer.max_download_bandwidth - chosen_peer.download_count_last_step, peer.upload_bandwidth-peer.upload_count_last_step )
                for _ in range(pieces_to_transfer):
                    if peer.upload_count_last_step < peer.upload_bandwidth:  # Check if peer can still upload
                        piece = available_pieces[0]
                        self.piece_freq[piece]+=1
                        chosen_peer.pieces.add(piece)
                        chosen_peer.download_count_last_step += 1
                        chosen_peer.downloaded_pieces += 1
                        peer.upload_count_last_step += 1
                        peer.uploaded_pieces += 1
                        available_pieces.remove(piece)
                        if len(chosen_peer.pieces) == file_len and not chosen_peer.is_seeder:
                            chosen_peer.is_seeder = True
                            chosen_peer.completed_step = current_step

    def print_summary(self):
        u_100_200 = 0
        u_200_300 = 0
        u_300_400 = 0
        u_400_500 = 0
        u_500_600 = 0
        u_600_700 = 0
        u_700_800 = 0
        n_100_200 = 0
        n_200_300 = 0
        n_300_400 = 0
        n_400_500 = 0
        n_500_600 = 0
        n_600_700 = 0
        n_700_800 = 0
        for peer in self.peers:
            if peer.upload_rate<200:
                u_100_200+=peer.completed_step
                n_100_200+=1
            elif peer.upload_rate<300:
                u_200_300+=peer.completed_step
                n_200_300+=1
            elif peer.upload_rate<400:
                u_300_400+=peer.completed_step
                n_300_400+=1
            elif peer.upload_rate<500:
                u_400_500+=peer.completed_step
                n_400_500+=1
            elif peer.upload_rate<600:
                u_500_600+=peer.completed_step
                n_500_600+=1
            elif peer.upload_rate<700:
                u_600_700+=peer.completed_step
                n_600_700+=1
            elif peer.upload_rate<800:
                u_700_800+=peer.completed_step
                n_700_800+=1
        if n_100_200:
            print(f"Average completion step for upload rate of 100-200 {u_100_200/n_100_200}")
        if n_200_300:
            print(f"Average completion step for upload rate of 200-300 {u_200_300/n_200_300}")
        if n_300_400:
            print(f"Average completion step for upload rate of 300-400 {u_300_400/n_300_400}")
        if n_400_500:
            print(f"Average completion step for upload rate of 400-500 {u_400_500/n_400_500}")
        if n_500_600:
            print(f"Average completion step for upload rate of 500-600 {u_500_600/n_500_600}")
        if n_600_700:
            print(f"Average completion step for upload rate of 600-700 {u_600_700/n_600_700}")
        if n_700_800:
            print(f"Average completion step for upload rate of 700-800 {u_700_800/n_700_800}")

    def plot_graph(self):
        completion_steps = {}
        upload_speed_ranges = [(100, 200), (200, 300), (300, 400), (400, 500), (500, 600), (600, 700), (700, 800)]
        
        # Initialize completion_steps with empty lists
        for speed_range in upload_speed_ranges:
            completion_steps[speed_range] = []

        # Populate completion_steps with completion steps for each upload speed range
        for peer in self.peers:
            for speed_range in upload_speed_ranges:
                if speed_range[0] <= peer.upload_rate < speed_range[1]:
                    completion_steps[speed_range].append(peer.completed_step)

        # Calculate average completion steps for each speed range
        avg_completion_steps = {speed_range: sum(steps) / len(steps) if steps else 0
                                for speed_range, steps in completion_steps.items()}

        # Plotting histogram
        speed_ranges_str = [f"{speed_range[0]}-{speed_range[1]}" for speed_range in upload_speed_ranges]
        plt.bar(speed_ranges_str, avg_completion_steps.values(), color='skyblue')
        plt.xlabel('Upload Speed Ranges')
        plt.ylabel('Average Completion Steps')
        plt.title('Average Completion Steps vs Upload Speed Ranges')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
    
    def print_statistics(self):
        # Calculate total pieces uploaded and downloaded
        total_uploaded_pieces = sum(peer.uploaded_pieces for peer in self.peers)
        total_downloaded_pieces = sum(peer.downloaded_pieces for peer in self.peers)

        # Calculate the median of the ratio of total pieces uploaded and downloaded
        upload_download_ratio = [peer.uploaded_pieces / (peer.downloaded_pieces + 1) for peer in self.peers]
        median_ratio = np.median(upload_download_ratio)

        print(f"\n\nTotal Uploaded Pieces: {total_uploaded_pieces}")
        print(f"Total Downloaded Pieces: {total_downloaded_pieces}")
        print(f"Median of the Ratio of Total Uploaded Pieces to Total Downloaded Pieces: {median_ratio}")



    def simulate(self):
        steps = 0
        while not self.all_have_files():
            self.perform_choke_unchoke(steps)
            # print(f"Step {steps}:")
            # for peer in self.peers:
            #     # print(peer)
            #     peer.adjust_upload_rate()
            steps += 1
            if steps > 2000:  
                print("Stopping simulation after 200 steps")
                break
        # for peer in self.peers:
        #     print(peer)
        self.print_summary()
        self.print_statistics()
        self.plot_graph()

network = TorrentNetwork()
network.simulate()
