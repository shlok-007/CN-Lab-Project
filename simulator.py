import random

class Simulation:

    class Agent:
        def __init__(self, id):

            self.id = id

            self.my_files = dict()
            # Initialize variables u/d ratio using normal distribution
            # self.u_d_ratio = random.gauss(0, 1)
            
            # probability of agent downloading a file from another agent each iteration
            self.p_down = random.gauss(0.1, 0.2)
            
            # Set is_seeded flag
            # self.is_seeded = False
            
            # Seed file number if is_seeded is True
            # self.seed_files = []
            # self.file_size = 50  #in terms of no. of blocks/chunks
            # self.files =dict()
            # for i in self.files_needed:
            #     self.files[i] = [0]*self.file_size

            self.file_needed = dict()

        def generate_file_need(self, all_files):
            # select one file randomly from all_files which is not already present in my_files
            needed_file = random.choice([i for i in all_files if i not in self.my_files.keys()])
            self.file_needed[needed_file] = [i+1 for i in range(all_files[needed_file])]
            self.my_files[needed_file] = []

        def download_chunk(self, fileID, chunkID):
            self.my_files[fileID].append(chunkID)
            self.file_needed[fileID].remove(chunkID)
            if len(self.file_needed[fileID]) == 0:
                del self.file_needed[fileID]

    def __init__(self):

        self.sim_iters = 1000

        self.total_down = 0
        self.total_up = 0

        self.min_dist = 1
        self.max_dist = 100

        self.num_files = 0
        self.p_file_spawn = 0.05 # Probability of spawning a new file each agent each iteration
        self.files = dict()
        self.max_file_chunks = 15
        self.tracker = dict()

        self.num_agents = 50
        # Create a list of Agent objects with size equal to num_agents
        self.agent_list = [self.Agent(_) for _ in range(self.num_agents)]
        
        # Assign each agent as the seeder for a randomly selected file
        for file in range(1, self.num_files+1):
            seeder = random.randint(1, self.num_agents)
            self.agent_list[seeder].is_seeded = True
            self.agent_list[seeder].seed_files.append(file)

        self.network = self.generate_network(self.agent_list)

    def generate_network(self):
        num_agents = len(self.agent_list)
        
        # Initialize an empty adjacency matrix
        adjacency_matrix = [[0] * num_agents for _ in range(num_agents)]
        
        # Generate random distances between agents and fill the adjacency matrix
        for i in range(num_agents):
            for j in range(i+1, num_agents):
                distance = random.randint(self.min_dist, self.max_dist)  # Random distance
                adjacency_matrix[i][j] = distance
                adjacency_matrix[j][i] = distance
        
        return adjacency_matrix
    
    def spawn_file(self):
        fileID = self.num_files
        self.num_files += 1
        self.files[fileID] = random.randint(1, self.max_file_chunks)
        # assigning the file to a random agent
        agent = random.randint(0, self.num_agents-1)
        # assign all the chunks of the file to the agent
        self.agent_list[agent].my_files[fileID] = [ i+1 for i in range(self.files[fileID])]
        for i in range(self.files[fileID]):
            self.tracker[(fileID, i+1)] = [agent]
        return agent, fileID
    
    def simulate(self):
        for i in range(self.sim_iters):
            # Spawn a new file with probability p_file_spawn
            if random.random() < self.p_file_spawn:
                agent, fileID = self.spawn_file()
                print(f"File {fileID} spawned by agent {agent}")
            
            # Generate file need for each agent
            for agent in self.agent_list:
                if(agent.file_needed == {} and random.random() < agent.p_down):
                    agent.generate_file_need(self.files)
            
            # Download chunks
            for agent in self.agent_list:
                for fileID, chunks in agent.file_needed.items():
                    for chunk in chunks:
                        if random.random() < agent.p_down:
                            agent.download_chunk(fileID, chunk)
                            self.total_down += 1
                            self.total_up += 1