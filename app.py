
from flask import Flask, render_template, request, redirect, url_for, session, g,send_file,jsonify
import sqlite3
import os
import requests
from bs4 import BeautifulSoup
from functools import wraps
import yt_dlp
import re
import requests
import json
import cohere

from flask import Flask, render_template, request, redirect, url_for, session, g,send_file
import sqlite3
import os
import requests
from bs4 import BeautifulSoup
from functools import wraps
import yt_dlp
import re
import requests
import json
import cohere

from flask import Flask, render_template, request, redirect, url_for, session, g,send_file
import sqlite3
from collections import defaultdict

import os
import requests
from bs4 import BeautifulSoup
from functools import wraps
import yt_dlp
import re
import requests
import json
import cohere
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Set a strong secret key in production
DATABASE = "app.db"


# ---------------- Database Helpers ----------------
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                xp_points INTEGER DEFAULT 0
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS extra (
                name TEXT PRIMARY KEY,
                score INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    topic_key TEXT NOT NULL,
    notes_viewed INTEGER DEFAULT 0,
    videos_viewed INTEGER DEFAULT 0,
    quiz_completed INTEGER DEFAULT 0,
    UNIQUE(username, topic_key)
);

        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_key TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                url TEXT NOT NULL,
                source TEXT,
                added_by TEXT,
                verified INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            note TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

# Initialize DB if needed on startup
if not os.path.exists(DATABASE):
    init_db()
    
    
    
NOTES_FILES = {
    "cse_gate": r"C:\Users\Arunava Chakraborty\Desktop\Scholar_Nest\GATE-CSE-notes-main.zip",
    "ece_gate": r"C:\Users\Arunava Chakraborty\Desktop\Scholar_Nest\Electronics-and-Communication-master1.zip",
    "dsa_preparation": r"C:\Users\Arunava Chakraborty\Desktop\Scholar_Nest\Data-Structures-and-Algorithms-Notes-main.zip"
}



@app.route("/buy_notes", methods=["GET", "POST"])
def buy_notes():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    if not user:
        return redirect(url_for("login"))

    if request.method == "POST":
        domain = request.form["domain"]
        email = request.form["email"]

        if user["xp_points"] >= 1000:
            drive_links = {
                "cse_gate": "https://drive.google.com/file/d/17SIbZD4snYyyd_sXhOtLjWBEOgyKguD1/view?usp=sharing",
                "ece_gate": "https://drive.google.com/file/d/1felxsSutnO_bij49V8ApsknGy4MHsvUr/view?usp=sharing",
                "dsa_preparation": "https://drive.google.com/file/d/1T3q1YSumAGOkM5v9wkO9nJ1mzuPpBhzi/view?usp=sharing",
            }

            drive_link = drive_links.get(domain)

            if drive_link:
                # Deduct 1000 points
                conn.execute(
                    "UPDATE users SET xp_points = xp_points - 1000 WHERE username = ?",
                    (username,)
                )
                conn.commit()

                # TODO: Here integrate Google Drive API to add email permission
                # For now, just show them the link
                confirmation = f"Success! The notes have been shared with {email}.<br>" \
                               f"Access your notes here: <a href='{drive_link}' target='_blank'>Open Notes</a>"

                return render_template(
                    "buy_notes.html",
                    confirmation=confirmation,
                    points=user["xp_points"]
                )

            else:
                return render_template(
                    "buy_notes.html",
                    confirmation="Notes link not found.",
                    points=user["xp_points"]
                )
        else:
            return render_template(
                "buy_notes.html",
                confirmation="Not enough points! You need at least 1000.",
                points=user["xp_points"]
            )

    return render_template("buy_notes.html", points=user["xp_points"])



    
    
    
    
    
    
import urllib.parse
from datetime import datetime
# YouTube API config (set env var YOUTUBE_API_KEY)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "AIzaSyAUAKwtm5zbLwDHkO55RFtI_Wnv1yv2n6g")

def fetch_youtube_videos(query, max_results=5):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "maxResults": max_results,
        "type": "video",
        "key": YOUTUBE_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    videos = []
    for item in data.get("items", []):
        videos.append({
            "title": item["snippet"]["title"],
            "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
            "video_id": item["id"]["videoId"]
        })
    return videos



# ---------------- Before Request Hook ----------------
@app.before_request
def load_logged_in_user():
    g.user = session.get("user")

# ---------------- XP helper functions ----------------







# ------------ Full Data -------------
ece_data = {  "Signals & Systems": {
        "Continuous-Time Signals": {
            "topic_key": "Signal_(electrical_engineering)",
            "questions": [
                ("Fourier Series Basics", "https://en.wikipedia.org/wiki/Fourier_series"),
                ("Laplace Transform Intro", "https://en.wikipedia.org/wiki/Laplace_transform"),
            ]
        },
        "Discrete-Time Signals": {
            "topic_key": "Discrete-time_signal",
            "questions": [
                ("Z-Transform", "https://en.wikipedia.org/wiki/Z-transform"),
            ]
        },
        "System Properties": {
            "topic_key": "System_theory",
            "questions": [
                ("LTI Systems", "https://en.wikipedia.org/wiki/Linear_time-invariant_system"),
            ]
        }
    },
    "Electronic Devices": {
        "Semiconductor Physics": {
            "topic_key": "Semiconductor",
            "questions": [
                ("PN Junction Theory", "https://en.wikipedia.org/wiki/P%E2%80%93n_junction"),
            ]
        },
        "Diodes & Applications": {
            "topic_key": "Diode",
            "questions": [
                ("Zener Diode Regulation", "https://en.wikipedia.org/wiki/Zener_diode"),
            ]
        },
        "Transistors": {
            "topic_key": "Bipolar_junction_transistor",
            "questions": [
                ("BJT Biasing", "https://en.wikipedia.org/wiki/Bipolar_junction_transistor"),
                ("MOSFET Basics", "https://en.wikipedia.org/wiki/MOSFET"),
            ]
        }
    },
    "Digital Electronics": {
        "Number Systems": {
            "topic_key": "Numeral_system",
            "questions": [
                ("Binary to Decimal Conversion", "https://en.wikipedia.org/wiki/Binary_number"),
            ]
        },
        "Logic Gates": {
            "topic_key": "Logic_gate",
            "questions": [
                ("Karnaugh Map Simplification", "https://en.wikipedia.org/wiki/Karnaugh_map"),
            ]
        },
        "Sequential Circuits": {
            "topic_key": "Sequential_logic",
            "questions": [
                ("Flip-Flop Types", "https://en.wikipedia.org/wiki/Flip-flop_(electronics)"),
            ]
        }
    },
    "Communication Systems": {
        "Analog Modulation": {
            "topic_key": "Amplitude_modulation",
            "questions": [
                ("AM Fundamentals", "https://en.wikipedia.org/wiki/Amplitude_modulation"),
                ("Frequency Modulation", "https://en.wikipedia.org/wiki/Frequency_modulation"),
            ]
        },
        "Digital Modulation": {
            "topic_key": "Phase-shift_keying",
            "questions": [
                ("PSK Modulation", "https://en.wikipedia.org/wiki/Phase-shift_keying"),
            ]
        },
        "Information Theory": {
            "topic_key": "Information_theory",
            "questions": [
                ("Shannon Capacity", "https://en.wikipedia.org/wiki/Shannon%E2%80%93Hartley_theorem"),
            ]
        }
    },
    "Control Systems": {
        "System Modeling": {
            "topic_key": "Control_system",
            "questions": [
                ("Transfer Function Basics", "https://en.wikipedia.org/wiki/Transfer_function"),
            ]
        },
        "Stability Analysis": {
            "topic_key": "Stability_theory",
            "questions": [
                ("Routh-Hurwitz", "https://en.wikipedia.org/wiki/Routh%E2%80%93Hurwitz_stability_criterion"),
            ]
        },
        "Time & Frequency Domain": {
            "topic_key": "Frequency_response",
            "questions": [
                ("Bode Plot", "https://en.wikipedia.org/wiki/Bode_plot"),
            ]
        }
    },
    "Microprocessors & Microcontrollers": {
        "8085 Architecture": {
            "topic_key": "Intel_8085",
            "questions": [
                ("Instruction Set", "https://en.wikipedia.org/wiki/Intel_8085"),
            ]
        },
        "8051 Microcontroller": {
            "topic_key": "Intel_8051",
            "questions": [
                ("Timers & Interrupts", "https://en.wikipedia.org/wiki/Intel_MCS-51"),
            ]
        },
        "ARM Processors": {
            "topic_key": "ARM_architecture",
            "questions": [
                ("ARM Instruction Set", "https://en.wikipedia.org/wiki/ARM_architecture"),
            ]
        }
    }
 }  # use full ECE dictionary from before
dsa_data = { "Arrays": {
        "Static vs Dynamic Arrays": {
            "topic_key": "Array_%28data_structure%29",
            "questions": [
                ("Reverse an Array", "https://leetcode.com/problems/reverse-string/"),
                ("Dynamic Array Explanation", "https://en.wikipedia.org/wiki/Dynamic_array")
            ]
        },
        "Prefix Sum": {
            "topic_key": "Prefix_sum",
            "questions": [
                ("Maximum Subarray (Kadane)", "https://leetcode.com/problems/maximum-subarray/"),
            ]
        },
        "Sliding Window": {
            "topic_key": "Sliding_window_algorithm",
            "questions": [
                ("Longest Substring without Repeating Characters", "https://leetcode.com/problems/longest-substring-without-repeating-characters/"),
            ]
        },
        "Two-Pointer Technique": {
            "topic_key": "Two-pointer_technique",
            "questions": [
                ("Container With Most Water", "https://leetcode.com/problems/container-with-most-water/"),
            ]
        }
    },
    "Linked List": {
        "Singly Linked List": {
            "topic_key": "Linked_list",
            "questions": [
                ("Reverse Linked List", "https://leetcode.com/problems/reverse-linked-list/"),
            ]
        },
        "Doubly Linked List": {
            "topic_key": "Doubly_linked_list",
            "questions": [
                ("Design Browser History", "https://leetcode.com/problems/design-browser-history/"),
            ]
        },
        "Circular Linked List": {
            "topic_key": "Circular_linked_list",
            "questions": [
                ("Josephus Problem", "https://leetcode.com/problems/josephus-problem/"),
            ]
        },
        "Fast & Slow Pointer": {
            "topic_key": "Floyd%27s_cycle-finding_algorithm",
            "questions": [
                ("Detect Cycle in Linked List", "https://leetcode.com/problems/linked-list-cycle/"),
            ]
        }
    },
    "Stack & Queue": {
        "Stack": {
            "topic_key": "Stack_%28abstract_data_type%29",
            "questions": [
                ("Min Stack", "https://leetcode.com/problems/min-stack/"),
            ]
        },
        "Queue & Deque": {
            "topic_key": "Queue_%28abstract_data_type%29",
            "questions": [
                ("Implement Queue using Stacks", "https://leetcode.com/problems/implement-queue-using-stacks/"),
            ]
        },
        "Monotonic Stack": {
            "topic_key": "Monotonic_queue",
            "questions": [
                ("Largest Rectangle in Histogram", "https://leetcode.com/problems/largest-rectangle-in-histogram/"),
            ]
        }
    },
    "Binary Search": {
        "Standard Binary Search": {
            "topic_key": "Binary_search_algorithm",
            "questions": [
                ("Binary Search", "https://leetcode.com/problems/binary-search/"),
            ]
        },
        "Rotated Array Search": {
            "topic_key": "Binary_search#Search_pattern_in_rotated_array",
            "questions": [
                ("Search in Rotated Sorted Array", "https://leetcode.com/problems/search-in-rotated-sorted-array/"),
            ]
        },
        "Bounds Finding": {
            "topic_key": "Binary_search_algorithm#Finding_boundaries",
            "questions": [
                ("Find First and Last Position", "https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/"),
            ]
        }
    },
    "Recursion & Backtracking": {
        "Basic Recursion": {
            "topic_key": "Recursion_%28computer_science%29",
            "questions": [
                ("Fibonacci Number", "https://leetcode.com/problems/fibonacci-number/"),
            ]
        },
        "Backtracking Patterns": {
            "topic_key": "Backtracking",
            "questions": [
                ("N-Queens", "https://leetcode.com/problems/n-queens/"),
            ]
        }
    },
    "Dynamic Programming": {
        "Knapsack": {
            "topic_key": "Knapsack_problem",
            "questions": [
                ("0/1 Knapsack Problem", "https://www.geeksforgeeks.org/0-1-knapsack-problem/"),
            ]
        },
        "LCS / Edit Distance": {
            "topic_key": "Longest_common_subsequence",
            "questions": [
                ("Longest Common Subsequence", "https://leetcode.com/problems/longest-common-subsequence/"),
                ("Edit Distance", "https://leetcode.com/problems/edit-distance/")
            ]
        }
    },
    "Graphs": {
        "BFS / DFS": {
            "topic_key": "Breadth-first_search",
            "questions": [
                ("Number of Islands", "https://leetcode.com/problems/number-of-islands/"),
            ]
        },
        "Shortest Path Algorithms": {
            "topic_key": "Dijkstra%27s_algorithm",
            "questions": [
                ("Network Delay Time", "https://leetcode.com/problems/network-delay-time/"),
            ]
        },
        "MST": {
            "topic_key": "Minimum_spanning_tree",
            "questions": [
                ("Kruskal / Prim Concepts", "https://en.wikipedia.org/wiki/Minimum_spanning_tree"),
            ]
        }
    },
    "Trees": {
        "Binary Tree": {
            "topic_key": "Binary_tree",
            "questions": [
                ("Inorder Traversal", "https://leetcode.com/problems/binary-tree-inorder-traversal/"),
            ]
        },
        "BST": {
            "topic_key": "Binary_search_tree",
            "questions": [
                ("Validate BST", "https://leetcode.com/problems/validate-binary-search-tree/"),
            ]
        },
        "AVL Tree": {
            "topic_key": "AVL_tree",
            "questions": [
                ("AVL Tree Insertion", "https://en.wikipedia.org/wiki/AVL_tree"),
            ]
        }
    } }  # use full DSA dictionary from before
cse_data = {
    "Programming Fundamentals": {
        "C Programming": {
            "topic_key": "C_(programming_language)",
            "questions": [
                ("Hello World & Basics", "https://www.programiz.com/c-programming/c-hello-world"),
                ("Pointers in C", "https://www.geeksforgeeks.org/pointers-in-c-and-cpp/"),
            ]
        },
        "C++": {
            "topic_key": "C%2B%2B",
            "questions": [
                ("STL Overview", "https://www.geeksforgeeks.org/the-c-standard-template-library-stl/"),
                ("OOP & Templates", "https://en.wikipedia.org/wiki/Template_(C%2B%2B)"),
            ]
        },
        "Java": {
            "topic_key": "Java_(programming_language)",
            "questions": [
                ("OOP in Java", "https://www.geeksforgeeks.org/object-oriented-programming-oops-concept-in-java/"),
            ]
        },
        "Python": {
            "topic_key": "Python_(programming_language)",
            "questions": [
                ("Python Basics", "https://www.w3schools.com/python/"),
                ("Python for Data Science", "https://en.wikipedia.org/wiki/Data_science"),
            ]
        },
    },

    "Data Structures & Algorithms": {
        "Arrays & Strings": {
            "topic_key": "Array_(data_structure)",
            "questions": [
                ("Array operations", "https://www.geeksforgeeks.org/array-data-structure/"),
                ("String algorithms", "https://en.wikipedia.org/wiki/String_(computer_science)"),
            ]
        },
        "Linked Lists": {
            "topic_key": "Linked_list",
            "questions": [
                ("Singly/Doubly/Circular", "https://www.geeksforgeeks.org/types-of-linked-list/"),
            ]
        },
        "Stacks & Queues": {
            "topic_key": "Stack_(abstract_data_type)",
            "questions": [
                ("Applications", "https://en.wikipedia.org/wiki/Stack_(abstract_data_type)"),
            ]
        },
        "Trees & Heaps": {
            "topic_key": "Tree_(data_structure)",
            "questions": [
                ("Binary Trees / Heaps", "https://www.geeksforgeeks.org/binary-tree-data-structure/"),
            ]
        },
        "Graphs": {
            "topic_key": "Graph_(abstract_data_type)",
            "questions": [
                ("BFS / DFS / Shortest Paths", "https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/"),
            ]
        },
        "Dynamic Programming": {
            "topic_key": "Dynamic_programming",
            "questions": [
                ("DP Patterns & Examples", "https://www.geeksforgeeks.org/dynamic-programming/"),
            ]
        },
        "Complexity & Analysis": {
            "topic_key": "Computational_complexity_theory",
            "questions": [
                ("Big-O, Time & Space", "https://en.wikipedia.org/wiki/Big_O_notation"),
            ]
        }
    },

    "Computer Architecture & Organization": {
        "Digital Logic": {
            "topic_key": "Digital_logic",
            "questions": [
                ("Boolean Algebra, Gates", "https://en.wikipedia.org/wiki/Boolean_algebra"),
            ]
        },
        "CPU Organization": {
            "topic_key": "Computer_architecture",
            "questions": [
                ("Von Neumann Model", "https://en.wikipedia.org/wiki/Von_Neumann_architecture"),
            ]
        },
        "Pipelining & Hazards": {
            "topic_key": "Instruction_pipelining",
            "questions": [
                ("Pipeline Stages & Hazards", "https://en.wikipedia.org/wiki/Pipeline_stall"),
            ]
        },
        "Memory Systems": {
            "topic_key": "Memory_hierarchy",
            "questions": [
                ("Cache, Virtual Memory", "https://en.wikipedia.org/wiki/CPU_cache"),
            ]
        },
        "Instruction Set Design": {
            "topic_key": "Instruction_set",
            "questions": [
                ("RISC vs CISC", "https://en.wikipedia.org/wiki/RISC"),
            ]
        }
    },

    "Operating Systems": {
        "Processes & Threads": {
            "topic_key": "Process_(computing)",
            "questions": [
                ("Process vs Thread", "https://en.wikipedia.org/wiki/Thread_(computing)"),
            ]
        },
        "Scheduling": {
            "topic_key": "Scheduling_(computing)",
            "questions": [
                ("RR, SJF, Priority", "https://en.wikipedia.org/wiki/Scheduling_(computing)"),
            ]
        },
        "Memory Management": {
            "topic_key": "Memory_management",
            "questions": [
                ("Paging, Segmentation", "https://en.wikipedia.org/wiki/Memory_segmentation"),
            ]
        },
        "File Systems & I/O": {
            "topic_key": "File_system",
            "questions": [
                ("File system concepts", "https://en.wikipedia.org/wiki/File_system"),
            ]
        },
        "Concurrency & Synchronization": {
            "topic_key": "Concurrency_(computer_science)",
            "questions": [
                ("Mutexes, Semaphores", "https://en.wikipedia.org/wiki/Semaphore_(programming)"),
            ]
        }
    },

    "Databases": {
        "Relational Databases": {
            "topic_key": "Relational_database",
            "questions": [
                ("SQL Basics", "https://www.w3schools.com/sql/"),
            ]
        },
        "NoSQL & NewSQL": {
            "topic_key": "NoSQL",
            "questions": [
                ("Document, Key-Value, Column Stores", "https://en.wikipedia.org/wiki/NoSQL"),
            ]
        },
        "Transactions & Concurrency": {
            "topic_key": "Database_transaction",
            "questions": [
                ("ACID & Isolation Levels", "https://en.wikipedia.org/wiki/ACID"),
            ]
        },
        "Data Modeling & Normalization": {
            "topic_key": "Database_normalization",
            "questions": [
                ("Normal Forms", "https://en.wikipedia.org/wiki/Database_normalization"),
            ]
        },
        "Indexing & Query Optimization": {
            "topic_key": "Database_index",
            "questions": [
                ("B-tree, Hash Indexes", "https://en.wikipedia.org/wiki/B-tree"),
            ]
        }
    },

    "Computer Networks": {
        "OSI & TCP/IP Models": {
            "topic_key": "OSI_model",
            "questions": [
                ("Layer Functions", "https://en.wikipedia.org/wiki/OSI_model"),
            ]
        },
        "Transport Layer": {
            "topic_key": "Transmission_Control_Protocol",
            "questions": [
                ("TCP vs UDP", "https://en.wikipedia.org/wiki/Transmission_Control_Protocol"),
            ]
        },
        "Routing & Switching": {
            "topic_key": "Routing",
            "questions": [
                ("Routing Algorithms", "https://en.wikipedia.org/wiki/Routing"),
            ]
        },
        "Network Security": {
            "topic_key": "Computer_security",
            "questions": [
                ("TLS, VPNs, Firewalls", "https://en.wikipedia.org/wiki/Transport_Layer_Security"),
            ]
        },
        "Wireless & Mobile Networks": {
            "topic_key": "Wireless_communication",
            "questions": [
                ("Wi-Fi, Cellular", "https://en.wikipedia.org/wiki/Wireless_network"),
            ]
        }
    },

    "Software Engineering & DevOps": {
        "Software Process Models": {
            "topic_key": "Systems_development_life_cycle",
            "questions": [
                ("Waterfall vs Agile", "https://en.wikipedia.org/wiki/Systems_development_life_cycle"),
            ]
        },
        "Design Patterns & Architecture": {
            "topic_key": "Software_architecture",
            "questions": [
                ("MVC, Microservices", "https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller"),
            ]
        },
        "Testing & QA": {
            "topic_key": "Software_testing",
            "questions": [
                ("Unit / Integration / System", "https://en.wikipedia.org/wiki/Software_testing"),
            ]
        },
        "DevOps & CI/CD": {
            "topic_key": "DevOps",
            "questions": [
                ("Continuous Integration / Delivery", "https://en.wikipedia.org/wiki/Continuous_delivery"),
            ]
        }
    },

    "Artificial Intelligence & ML": {
        "Machine Learning": {
            "topic_key": "Machine_learning",
            "questions": [
                ("Supervised vs Unsupervised", "https://en.wikipedia.org/wiki/Machine_learning"),
            ]
        },
        "Deep Learning": {
            "topic_key": "Deep_learning",
            "questions": [
                ("Neural Networks & CNNs", "https://en.wikipedia.org/wiki/Convolutional_neural_network"),
            ]
        },
        "NLP": {
            "topic_key": "Natural_language_processing",
            "questions": [
                ("Tokenization, Transformers", "https://en.wikipedia.org/wiki/Transformer_(machine_learning_model)"),
            ]
        },
        "Reinforcement Learning": {
            "topic_key": "Reinforcement_learning",
            "questions": [
                ("Q-Learning, Policy Gradients", "https://en.wikipedia.org/wiki/Reinforcement_learning"),
            ]
        }
    },

    "Theory of Computation & Compilers": {
        "Automata Theory": {
            "topic_key": "Automata_theory",
            "questions": [
                ("DFA, NFA, Regular Expressions", "https://en.wikipedia.org/wiki/Automata_theory"),
            ]
        },
        "Computability & Complexity": {
            "topic_key": "Computational_complexity_theory",
            "questions": [
                ("P vs NP, Reductions", "https://en.wikipedia.org/wiki/P_versus_NP_problem"),
            ]
        },
        "Compiler Design": {
            "topic_key": "Compiler",
            "questions": [
                ("Lexing, Parsing, Code Gen", "https://en.wikipedia.org/wiki/Compiler"),
            ]
        }
    },

    "Human-Computer Interaction & Graphics": {
        "HCI Principles": {
            "topic_key": "Human%E2%80%93computer_interaction",
            "questions": [
                ("Usability, UX Basics", "https://en.wikipedia.org/wiki/User_experience"),
            ]
        },
        "Computer Graphics": {
            "topic_key": "Computer_graphics",
            "questions": [
                ("Rasterization, Shaders", "https://en.wikipedia.org/wiki/Computer_graphics"),
            ]
        },
        "Visualization": {
            "topic_key": "Information_visualization",
            "questions": [
                ("Data Viz Techniques", "https://en.wikipedia.org/wiki/Information_visualization"),
            ]
        }
    },

    "Distributed Systems & Cloud": {
        "Distributed Systems": {
            "topic_key": "Distributed_computing",
            "questions": [
                ("Consistency Models, CAP Theorem", "https://en.wikipedia.org/wiki/CAP_theorem"),
            ]
        },
        "Cloud Computing": {
            "topic_key": "Cloud_computing",
            "questions": [
                ("IaaS / PaaS / SaaS", "https://en.wikipedia.org/wiki/Cloud_computing"),
            ]
        },
        "Big Data & Hadoop": {
            "topic_key": "Big_data",
            "questions": [
                ("HDFS, MapReduce", "https://en.wikipedia.org/wiki/MapReduce"),
            ]
        }
    },

    "Security, Blockchain & Privacy": {
        "Cryptography": {
            "topic_key": "Cryptography",
            "questions": [
                ("Symmetric vs Asymmetric", "https://en.wikipedia.org/wiki/Cryptography"),
            ]
        },
        "Blockchain": {
            "topic_key": "Blockchain",
            "questions": [
                ("Consensus Mechanisms", "https://en.wikipedia.org/wiki/Blockchain"),
            ]
        },
        "Privacy & Ethics": {
            "topic_key": "Privacy_law",
            "questions": [
                ("Data Privacy basics", "https://en.wikipedia.org/wiki/Privacy"),
            ]
        }
    },

    "Mobile & Web Development": {
        "Web Development": {
            "topic_key": "Web_development",
            "questions": [
                ("HTML/CSS/JS basics", "https://developer.mozilla.org/en-US/docs/Learn"),
            ]
        },
        "Mobile Development": {
            "topic_key": "Mobile_app_development",
            "questions": [
                ("Android / iOS fundamentals", "https://en.wikipedia.org/wiki/Android_(operating_system)"),
            ]
        },
        "Progressive Web Apps": {
            "topic_key": "Progressive_web_app",
            "questions": [
                ("PWA Concepts", "https://en.wikipedia.org/wiki/Progressive_web_app"),
            ]
        }
    },

    "Emerging & Advanced Topics": {
        "Quantum Computing": {
            "topic_key": "Quantum_computing",
            "questions": [
                ("Qubits & Algorithms", "https://en.wikipedia.org/wiki/Quantum_computing"),
            ]
        },
        "Computer Vision": {
            "topic_key": "Computer_vision",
            "questions": [
                ("Image Processing & CNNs", "https://en.wikipedia.org/wiki/Computer_vision"),
            ]
        },
        "Robotics & Automation": {
            "topic_key": "Robotics",
            "questions": [
                ("Kinematics, Control", "https://en.wikipedia.org/wiki/Robotics"),
            ]
        }
    }
}
  # use full CSE dictionary from before

all_data = {
    "ECE": ece_data,
    "DSA": dsa_data,
    "CSE": cse_data
}
import google.generativeai as genai
import re
# --- Load your Gemini API key ---
genai.configure(api_key="AIzaSyBfvijC3DuUVEH5EH3ZV3zZAcXpnnwK5b8")
gemini_model = genai.GenerativeModel('gemini-1.5-flash')
import os
import pandas as pd
import xml.etree.ElementTree as ET
# --- Replace NER with simple keyword extraction ---
# --- Extract keywords from user input ---
def extract_keywords(text):
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    stopwords = {
        "what", "does", "mean", "the", "your", "with", "from", "that", "which",
        "have", "how", "and", "when", "then", "than", "into", "this", "about", "like"
    }
    keywords = [word for word in words if word not in stopwords]
    return list(set(keywords))
# Generate answer using Gemini
def generate_answer_with_gemini(question):
    try:
        response = gemini_model.generate_content(question)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "Sorry, I'm unable to answer that right now."
# ------------ Helpers -------------
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def fetch_wiki_notes(topic, max_paras=20, extra_pages=2):
    base_url = "https://en.wikipedia.org/wiki/"
    url = f"{base_url}{topic.replace(' ', '_')}"
    collected_text = []

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; StudyNotesBot/1.0; +https://yourdomain.com)"
    }

    def scrape_page(page_url, limit):
        try:
            print(f"[DEBUG] Scraping: {page_url}")
            res = requests.get(page_url, headers=headers, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                paras = soup.find_all('p')
                for p in paras:
                    text = p.get_text().strip()
                    if text and not text.startswith("Coordinates"):
                        collected_text.append(text)
                        if len(collected_text) >= limit:
                            return
            else:
                collected_text.append(f"⚠️ Could not fetch {page_url} (status {res.status_code})")
        except Exception as e:
            collected_text.append(f"❌ Error fetching {page_url}: {e}")

    # 1️⃣ Scrape the main topic page
    scrape_page(url, max_paras)

    # 2️⃣ Optionally scrape a few related Wikipedia links
    if extra_pages > 0:
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                links = soup.select("a[href^='/wiki/']")
                seen = set()
                for link in links:
                    href = link.get("href")
                    if ':' in href:  # skip non-article pages like "Category:" or "File:"
                        continue
                    full_url = urljoin(base_url, href)
                    if full_url not in seen:
                        seen.add(full_url)
                        scrape_page(full_url, max_paras * (extra_pages + 1))
                        extra_pages -= 1
                        if extra_pages <= 0:
                            break
        except Exception as e:
            collected_text.append(f"❌ Error fetching related pages: {e}")

    # Return notes
    return "\n\n".join(collected_text[:max_paras * (extra_pages + 1)])


# ----------------------------
# Find Domain and Topic Index
# ----------------------------
def find_topic_domain_and_index(topic_key):
    for domain_name, domain_topics in all_data.items():
        for idx, (topic_name, subs) in enumerate(domain_topics.items(), start=1):
            for sub_name, sub_info in subs.items():
                if sub_info.get("topic_key") == topic_key:
                    return domain_name, idx
    return "ECE", 1  # default fallback


# from transformers import pipeline

# # Force PyTorch backend, no TF dependency
# summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small", framework="pt")



# def get_clean_transcript(video_url):
#     try:
#         if "watch?v=" in video_url:
#             video_id = video_url.split("v=")[-1].split("&")[0]
#         elif "youtu.be/" in video_url:
#             video_id = video_url.split("/")[-1].split("?")[0]
#         else:
#             return None, "Invalid YouTube URL"

#         transcript_data = YouTubeTranscriptApi().fetch(video_id)

#         if isinstance(transcript_data, list):
#             full_text = " ".join([item['text'] for item in transcript_data])
#         else:
#             full_text = str(transcript_data)

#         return full_text, None
#     except Exception as e:
#         return None, f"❌ Error fetching transcript: {str(e)}"


# def clean_transcript_text(text):
#     text = re.sub(r'\[.*?\]', '', text)  # Remove things like [Music], [Applause], etc.
#     text = re.sub(r'\s+', ' ', text)     # Normalize multiple spaces
#     text = re.sub(r'[^a-zA-Z0-9.,?!\s]', '', text)  # Remove special chars
#     text = re.sub(r'\[Music\]', '', text)
#     text = re.sub(r'\s+', ' ', text)
#     text = text.strip()
#     text = text.replace('  ', ' ')
#     return text.strip()

# def summarize_text(text, max_chunk_length=1000):
#     text_chunks = [text[i:i + max_chunk_length] for i in range(0, len(text), max_chunk_length)]
#     summary = ""
#     for chunk in text_chunks:
#         try:
#             result = summarizer(chunk, max_length=120, min_length=30, do_sample=False)
#             summary += result[0]['summary_text'] + " "
#         except Exception as e:
#             summary += "[Summary Error] "
#     return summary.strip()

# =============== Groq / LangChain setup ===============
# pip install langchain langchain-groq



# ---------------- Routes ----------------

@app.route("/")
# @login_required
def home():
    return render_template("home.html")

@app.route("/profile/notes", methods=["GET", "POST"])
def user_notes():
    if not g.user:
        return redirect(url_for("login"))

    with get_db() as conn:
        if request.method == "POST":
            note_text = request.form.get("note", "").strip()
            if note_text:
                conn.execute(
                    "INSERT INTO notes (username, note) VALUES (?, ?)",
                    (g.user, note_text)
                )

        # Get all notes for this user
        cur = conn.execute(
            "SELECT note, updated_at FROM notes WHERE username=? ORDER BY updated_at DESC",
            (g.user,)
        )
        notes = cur.fetchall()

    return render_template("user_notes.html", notes=notes)

@app.route('/chatbot', methods=['GET', 'POST'])
@login_required
def chatbot():
    answer = None
    
    similarity = None  # Optional: in case you plan to add similarity score later

    if request.method == 'POST':
        user_input = request.form['question']
        keywords = extract_keywords(user_input)
        answer = generate_answer_with_gemini(user_input)
        

    return render_template(
        'chatbot.html',
        answer=answer,
        similarity=similarity,
        
    )
@app.route("/about")
def about():
    return render_template("about.html")

# Terms & Conditions page route
@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    if not g.user:
        return redirect(url_for("login"))

    if request.method == "POST":
        selected_domain = request.form.get("domain", "ECE")
    else:
        selected_domain = request.args.get("domain", "ECE")

    with get_db() as conn:
        cur = conn.execute("SELECT topic_key FROM progress WHERE username=? AND notes_viewed=1", (g.user,))
        completed = {row["topic_key"]: True for row in cur.fetchall()}

    return render_template(
        "index.html",
        data=all_data.get(selected_domain, {}),
        domains=list(all_data.keys()),
        selected_domain=selected_domain,
        completed=completed
    )
SERPAPI_API_KEY = "841974743a62583533f4b92aa78f79a8a60295de8477497531c4f37681af2483"
import time    
def clean_price(price_str):
    """Extract numeric price from string like '₹499'."""
    if not price_str:
        return None
    price_str = re.sub(r'[^\d.]', '', price_str)
    return float(price_str) if price_str else None

def fetch_top_books(topic, limit=5):
    """Fetch top N books for a topic from Amazon via SerpAPI."""
    params = {
        "api_key": SERPAPI_API_KEY,
        "engine": "amazon",
        "amazon_domain": "amazon.in",
        "k": topic
    }

    all_books = []
    for page in range(1, 2):  # First 2 pages
        params["page"] = page
        search = requests.get("https://serpapi.com/search", params=params)
        response = search.json()

        for result in response.get("organic_results", []):
            title = result.get("title")
            link = result.get("link")
            thumbnail = result.get("thumbnail")
            price = clean_price(result.get("price"))
            author = result.get("author") if "author" in result else None

            if title:
                all_books.append({
                    "title": title,
                    "author": author,
                    "price": price,
                    "image_path": thumbnail,
                    "product_link": link
                })
        time.sleep(1)

    # Sort by price if available, otherwise keep order
    all_books = sorted(all_books, key=lambda x: (x["price"] if x["price"] else float("inf")))
    return all_books[:limit]
# =============== MCQ Parsing ===============
def get_user_xp(username):
    with get_db() as conn:
        row = conn.execute(
            "SELECT xp_points FROM users WHERE username=?", (username,)
        ).fetchone()
        return row["xp_points"] if row else 0


def add_user_xp(username, points, conn=None):
    if conn is None:  # no active connection, open one
        with get_db() as conn:
            conn.execute(
                "UPDATE users SET xp_points = xp_points + ? WHERE username = ?",
                (points, username)
            )
            conn.commit()
    else:  # reuse existing connection
        conn.execute(
            "UPDATE users SET xp_points = xp_points + ? WHERE username = ?",
            (points, username)
        )



@app.context_processor
def inject_xp():
    user = getattr(g, 'user', None) or session.get('user')
    xp = get_user_xp(user) if user else 0
    return dict(xp=xp)


@app.route("/notes/<topic_key>")
@login_required
def notes(topic_key):
    # Save user progress
    with get_db() as conn:
        existing = conn.execute(
            "SELECT * FROM progress WHERE username=? AND topic_key=?",
            (g.user, topic_key)
        ).fetchone()

        if not existing:
            conn.execute(
                "INSERT INTO progress (username, topic_key, notes_viewed) VALUES (?, ?, 1)",
                (g.user, topic_key)
            )
            add_user_xp(g.user, 50, conn)  # Award 50 XP for first viewing
        else:
            conn.execute(
                "UPDATE progress SET notes_viewed=1 WHERE username=? AND topic_key=?",
                (g.user, topic_key)
            )
        conn.commit()

    # Find domain and index
    domain_name, topic_index = find_topic_domain_and_index(topic_key)

    # Fetch Wiki notes
    notes_text = fetch_wiki_notes(topic_key)
    if not notes_text.strip():
        notes_text = "⚠️ Sorry, no notes could be fetched for this topic."

    # Fetch top 5 books related to topic
    books = fetch_top_books(topic_key + " book", limit=5)

    return render_template(
        "notes.html",
        notes=notes_text,
        books=books,
        selected_domain=domain_name,
        topic_index=topic_index
    )

@app.route("/videos/<topic_key>")
@login_required
def videos(topic_key):
    with get_db() as conn:
        prog = conn.execute(
            "SELECT * FROM progress WHERE username=? AND topic_key=?", (g.user, topic_key)
        ).fetchone()

        if prog is None:
            conn.execute(
                "INSERT INTO progress (username, topic_key, videos_viewed) VALUES (?, ?, 1)",
                (g.user, topic_key)
            )
            add_user_xp(g.user, 75, conn)
        elif prog["videos_viewed"] == 0:
            conn.execute(
                "UPDATE progress SET videos_viewed=1 WHERE username=? AND topic_key=?",
                (g.user, topic_key)
            )
            add_user_xp(g.user, 75, conn)
        conn.commit()    

    domain_name, _ = find_topic_domain_and_index(topic_key)
    domain_topics = all_data.get(domain_name, {})
    topic_name = None
    for subs in domain_topics.values():
        for sub_name, sub_info in subs.items():
            if sub_info.get("topic_key") == topic_key:
                topic_name = sub_name
                break
        if topic_name:
            break

    if not topic_name:
        return "Topic not found", 404

    # YouTube Search API
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": topic_name,
        "type": "video",
        "maxResults": 5,
        "key": YOUTUBE_API_KEY
    }
    resp = requests.get(url, params=params)
    videos_data = resp.json().get("items", [])

    videos_list = [
        {
            "title": v["snippet"]["title"],
            "video_id": v["id"]["videoId"],
            "thumbnail": v["snippet"]["thumbnails"]["medium"]["url"]
        }
        for v in videos_data
    ]

    return render_template(
        "videos.html",
        topic_name=topic_name,
        videos=videos_list,
        selected_domain=domain_name
    )






user=None
@app.route("/login", methods=["GET", "POST"])
def login():
    global user
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        user=username
        with get_db() as conn:
            cur = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            if cur.fetchone():
                session["user"] = username
                session.permanent = True
                add_user_xp(username, 25, conn)   # Award 25 XP on login
                conn.commit()
                return redirect(url_for("home"))
        return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            return render_template("register.html", error="Username and password required")
        with get_db() as conn:
            try:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                return render_template("register.html", error="Username already exists")
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


#--------------------------------------------------------------------------------------------------------------------
import os
from flask import request, render_template, redirect, url_for, g
from fpdf import FPDF
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

NUM_QUESTIONS = 10
OUTPUT_FOLDER = "results"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# LangChain setup
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0.0
)



mcq_prompt = PromptTemplate(
    input_variables=["context", "num_questions"],
    template="""
You are an AI assistant helping generate multiple-choice questions (MCQs) from the text below.

Text:
{context}

Generate exactly {num_questions} MCQs.

Each MCQ must have:
- Question: [text]
- Four answer options labeled exactly A), B), C), D) on separate lines
- The correct answer at the end

Format:
## MCQ
Question: ...
A) ...
B) ...
C) ...
D) ...
Correct Answer: A/B/C/D
"""
)

mcq_chain = mcq_prompt | llm

def save_txt(mcqs, filename):
    path = os.path.join(OUTPUT_FOLDER, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(mcqs)
    print(f"✅ Saved text to {path}")

def save_pdf(mcqs, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for mcq in mcqs.split("## MCQ"):
        if mcq.strip():
            pdf.multi_cell(0, 10, mcq.strip())
            pdf.ln(5)
    path = os.path.join(OUTPUT_FOLDER, filename)
    pdf.output(path)
    print(f"✅ Saved PDF to {path}")

import re
from flask import request, render_template, redirect, url_for, g
# def download_subtitle_content(url):
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         return response.text
#     except Exception as e:
#         print(f"Error downloading subtitles: {e}")
#         return None

# def parse_vtt_content(vtt_content):
#     if not vtt_content:
#         return ""
#     lines = vtt_content.split("\n")
#     transcript_lines = []
#     for line in lines:
#         line = line.strip()
#         if (line.startswith("WEBVTT") or "-->" in line or not line or line.isdigit()):
#             continue
#         line = re.sub(r"<[^>]+>", "", line)
#         if line:
#             transcript_lines.append(line)
#     transcript = " ".join(transcript_lines)
#     return re.sub(r"\s+", " ", transcript).strip()

# def get_video_transcript(video_url):
#     ydl_opts = {
#     "skip_download": True,
#     "writesubtitles": True,
#     "writeautomaticsub": True,
#     "subtitleslangs": ["en"],
#     "quiet": True,
#     "format": "best"   # ✅ always pick best available format
# }

#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(video_url, download=False)
#             title = info.get("title", "Unknown Title")
#             uploader = info.get("uploader", "Unknown Channel")
#             subtitles = info.get("subtitles", {})
#             auto_captions = info.get("automatic_captions", {})

#             transcript_data = None
#             for lang in ["en", "en-US", "en-GB"]:
#                 if lang in subtitles:
#                     transcript_data = download_subtitle_content(subtitles[lang][0]["url"])
#                     break
#             if not transcript_data:
#                 for lang in ["en", "en-US", "en-GB"]:
#                     if lang in auto_captions:
#                         transcript_data = download_subtitle_content(auto_captions[lang][0]["url"])
#                         break

#             if not transcript_data:
#                 return None, title, uploader
#             return parse_vtt_content(transcript_data), title, uploader
#     except Exception as e:
#         print(f"Transcript error: {e}")
#         return None, "Unknown Title", "Unknown Channel"

# # -------------------- COHERE ANALYSIS FUNCTIONS --------------------

# class CohereTextAnalyzer:
#     def __init__(self, api_key: str):
#         self.co = cohere.Client(api_key)

#     def summarize_text(self, text: str) -> str:
#         try:
#             # ✅ Using Chat API (future-proof)
#             response = self.co.chat(
#                 model="command-r-plus",  # recommended model
#                 message=f"Summarize the following text in concise bullet points:\n\n{text}",
#                 temperature=0.3
#             )
#             return response.text
#         except Exception as e:
#             return f"Error summarizing: {e}"

# # Utility: Break large transcripts into smaller chunks
# def chunk_text(text, max_chars=8000):
#     chunks = []
#     while len(text) > max_chars:
#         split_at = text[:max_chars].rfind(" ")
#         if split_at == -1:
#             split_at = max_chars
#         chunks.append(text[:split_at])
#         text = text[split_at:]
#     chunks.append(text)
#     return chunks

# def summarize_long_text(analyzer, text):
#     chunks = chunk_text(text)
#     partial_summaries = []
#     for i, chunk in enumerate(chunks, 1):
#         print(f"Summarizing chunk {i}/{len(chunks)}...")
#         summary = analyzer.summarize_text(chunk)
#         partial_summaries.append(summary)
#     combined = "\n".join(partial_summaries)
#     return analyzer.summarize_text(combined)

# # -------------------- MAIN APP ROUTE --------------------
#######################################################################
from flask import Flask, render_template, request, jsonify
import traceback
import yt_dlp
import re
import json
import cohere
import os
from typing import Optional, List
import requests

# Initialize Cohere API key
COHERE_API_KEY = "Qha3099MMPmJNo8wuy84GhtIyueykygWtkMPErZg"  # Move to environment variable in production

def extract_video_id(url):
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
        r'youtube\.com/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def download_subtitle_content(url):
    """Download subtitle content from URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error downloading subtitles: {e}")
        return None

def parse_vtt_content(vtt_content):
    """Parse VTT subtitle content and extract text"""
    if not vtt_content:
        return ""
    
    # Check if it's JSON format (YouTube's internal format)
    if vtt_content.strip().startswith('{'):
        try:
            return parse_youtube_json_transcript(vtt_content)
        except:
            pass
    
    # Handle standard VTT format
    lines = vtt_content.split('\n')
    transcript_lines = []
    
    for line in lines:
        line = line.strip()
        
        # Skip VTT headers, timestamps, and empty lines
        if (line.startswith('WEBVTT') or 
            line.startswith('Kind:') or
            line.startswith('Language:') or
            '-->' in line or
            not line or
            line.isdigit()):
            continue
        
        # Remove HTML tags if present
        line = re.sub(r'<[^>]+>', '', line)
        
        # Remove timestamp info that might be embedded
        line = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3}', '', line)
        
        if line:
            transcript_lines.append(line)
    
    # Join lines and clean up
    transcript = ' '.join(transcript_lines)
    transcript = re.sub(r'\s+', ' ', transcript).strip()
    
    return transcript

def parse_youtube_json_transcript(json_content):
    """Parse YouTube's JSON transcript format"""
    try:
        data = json.loads(json_content)
        events = data.get('events', [])
        
        transcript_parts = []
        
        for event in events:
            segs = event.get('segs', [])
            for seg in segs:
                text = seg.get('utf8', '').strip()
                if text and text != '\n':
                    # Clean up common issues
                    text = text.replace('\u003e\u003e', '').strip()
                    if text:
                        transcript_parts.append(text)
        
        # Join all parts and clean up
        transcript = ' '.join(transcript_parts)
        transcript = re.sub(r'\s+', ' ', transcript).strip()
        
        return transcript
        
    except Exception as e:
        print(f"Error parsing JSON transcript: {e}")
        return ""

def get_video_transcript_yt_dlp(video_url):
    """Get transcript using yt-dlp (more reliable)"""
    
    try:
        # Configure yt-dlp options
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en', 'en-US', 'en-GB'],
            'subtitlesformat': 'vtt',
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info
            info = ydl.extract_info(video_url, download=False)
            
            title = info.get('title', 'Unknown Title')
            uploader = info.get('uploader', 'Unknown Channel')
            
            # Get subtitles
            subtitles = info.get('subtitles', {})
            automatic_captions = info.get('automatic_captions', {})
            
            # Try to find English subtitles
            transcript_data = None
            
            # First try manual subtitles
            for lang in ['en', 'en-US', 'en-GB']:
                if lang in subtitles:
                    subtitle_info = subtitles[lang][0]  # Get first format
                    transcript_data = download_subtitle_content(subtitle_info['url'])
                    break
            
            # If no manual subtitles, try automatic captions
            if not transcript_data:
                for lang in ['en', 'en-US', 'en-GB']:
                    if lang in automatic_captions:
                        subtitle_info = automatic_captions[lang][0]  # Get first format
                        transcript_data = download_subtitle_content(subtitle_info['url'])
                        break
            
            if not transcript_data:
                return None, "No English transcripts/captions available for this video"
            
            # Parse VTT content
            transcript_text = parse_vtt_content(transcript_data)
            
            return {
                'transcript': transcript_text,
                'title': title,
                'uploader': uploader
            }, None
            
    except Exception as e:
        return None, f"Error getting transcript: {str(e)}"

class CohereTextAnalyzer:
    def __init__(self, api_key: str):
        """Initialize Cohere client with API key"""
        self.co = cohere.Client(api_key)
    
    def summarize_text(self, text: str, length: str = 'medium', format_type: str = 'bullets') -> str:
        """Summarize text using Cohere's dedicated summarize endpoint"""
        try:
            response = self.co.summarize(
                text=text,
                length=length,
                format=format_type,
                model='summarize-xlarge',
                extractiveness='medium'
            )
            return response.summary
        except Exception as e:
            return f"Error: {e}"
    
    def generate_custom_summary(self, text: str, prompt_style: str = 'numbered') -> str:
        """Create custom summary using generate endpoint"""
        prompts = {
            'bullets': f"Summarize the following text into bullet points highlighting the most important topics:\n\n{text}\n\nKey Points:\n•",
            'numbered': f"Summarize the following text into a numbered list of key points:\n\n{text}\n\nSummary:\n1.",
            'paragraph': f"Provide a concise paragraph summary of the following text:\n\n{text}\n\nSummary:"
        }
        
        try:
            response = self.co.generate(
                model='command',
                prompt=prompts.get(prompt_style, prompts['numbered']),
                max_tokens=200,
                temperature=0.3,
                stop_sequences=['\n\n']
            )
            return response.generations[0].text.strip()
        except Exception as e:
            return f"Error: {e}"
    
    def extract_key_topics(self, text: str, num_topics: int = 5) -> str:
        """Extract key topics from text"""
        prompt = f"Extract the {num_topics} most important topics from this text:\n\n{text}\n\nKey Topics:\n1."
        
        try:
            response = self.co.generate(
                model='command',
                prompt=prompt,
                max_tokens=150,
                temperature=0.2
            )
            return response.generations[0].text.strip()
        except Exception as e:
            return f"Error: {e}"
    
    def extract_exact_meaning(self, text: str) -> str:
        """Extract the exact meaning, intent, and core message from the text"""
        prompt = f"""Analyze the following text and extract its exact meaning, core message, and underlying intent. Explain what the speakers are really trying to communicate:

{text}

Exact Meaning Analysis:"""
        
        try:
            response = self.co.generate(
                model='command',
                prompt=prompt,
                max_tokens=400,
                temperature=0.1
            )
            return response.generations[0].text.strip()
        except Exception as e:
            return f"Error: {e}"
    
    def extract_context_and_purpose(self, text: str) -> str:
        """Extract the context, purpose, and situational meaning from the text"""
        prompt = f"""Analyze this text to understand its exact context, purpose, and situational meaning:

{text}

Context and Purpose Analysis:"""
        
        try:
            response = self.co.generate(
                model='command',
                prompt=prompt,
                max_tokens=300,
                temperature=0.1
            )
            return response.generations[0].text.strip()
        except Exception as e:
            return f"Error: {e}"
    
    def extract_speaker_intentions(self, text: str) -> str:
        """Analyze what each speaker is trying to achieve or communicate"""
        prompt = f"""Analyze the following text and identify what each speaker is trying to achieve:

{text}

Speaker Intentions Analysis:"""
        
        try:
            response = self.co.generate(
                model='command',
                prompt=prompt,
                max_tokens=250,
                temperature=0.1
            )
            return response.generations[0].text.strip()
        except Exception as e:
            return f"Error: {e}"

# Flask Routes
@app.route("/transcript-analyzer", methods=["GET"])
def transcript_analyzer():
    """Render the transcript analyzer page"""
    return render_template("index_transcript.html")

@app.route("/analyze", methods=["POST"])
def analyze_video():
    """Analyze YouTube video transcript"""
    try:
        data = request.get_json()
        video_url = data.get('video_url', '').strip()
        
        if not video_url:
            return jsonify({
                'success': False,
                'error': 'Please provide a YouTube URL'
            })
        
        # Extract video ID to validate URL
        video_id = extract_video_id(video_url)
        if not video_id:
            return jsonify({
                'success': False,
                'error': 'Invalid YouTube URL format'
            })
        
        # Get transcript
        transcript_result, error = get_video_transcript_yt_dlp(video_url)
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            })
        
        transcript_text = transcript_result['transcript']
        
        if not transcript_text or len(transcript_text.strip()) < 50:
            return jsonify({
                'success': False,
                'error': 'Transcript too short or empty'
            })
        
        # Initialize analyzer
        analyzer = CohereTextAnalyzer(COHERE_API_KEY)
        
        # Perform analysis
        results = {}
        
        # Get different types of summaries and analysis
        results['bullet_point_summary'] = analyzer.summarize_text(transcript_text, format_type='bullets')
        results['paragraph_summary'] = analyzer.summarize_text(transcript_text, format_type='paragraph')
        results['key_topics'] = "1. " + analyzer.extract_key_topics(transcript_text, num_topics=5)
        results['exact_meaning_analysis'] = analyzer.extract_exact_meaning(transcript_text)
        results['context_purpose_analysis'] = analyzer.extract_context_and_purpose(transcript_text)
        results['speaker_intentions'] = analyzer.extract_speaker_intentions(transcript_text)
        results['numbered_summary'] = "1. " + analyzer.generate_custom_summary(transcript_text, 'numbered')
        
        # Return successful response
        return jsonify({
            'success': True,
            'video_url': video_url,
            'transcript_length': len(transcript_text),
            'video_title': transcript_result.get('title', 'Unknown Title'),
            'video_uploader': transcript_result.get('uploader', 'Unknown Channel'),
            'results': results
        })
        
    except Exception as e:
        print(f"Error in analyze_video: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'An error occurred during analysis: {str(e)}'
        })


#######################################################################
@app.route("/quiz/<topic_key>", methods=["GET", "POST"])
@login_required
def quiz(topic_key):
    if not g.user:
        return redirect(url_for("login"))

    # Find topic name
    domain_name, _ = find_topic_domain_and_index(topic_key)
    topic_name = None
    domain_topics = all_data.get(domain_name, {})
    for subs in domain_topics.values():
        for sub_name, sub_info in subs.items():
            if sub_info.get("topic_key") == topic_key:
                topic_name = sub_name
                break
        if topic_name:
            break

    if not topic_name:
        return "Topic not found", 404

    if request.method == "GET":
        # Fetch study notes
        study_text = fetch_wiki_notes(topic_key)
        if not study_text.strip():
            return "No study material found for this topic.", 404

        # Generate MCQs from LLM using new LangChain style
        mcqs_text = mcq_chain.invoke({"context": study_text, "num_questions": NUM_QUESTIONS})

# Extract string
        if hasattr(mcqs_text, "content"):
            mcqs_text = mcqs_text.content
        elif isinstance(mcqs_text, dict) and "text" in mcqs_text:
            mcqs_text = mcqs_text["text"]

        mcqs_text = mcqs_text.strip()
        print("=== Raw MCQs from LLM ===")
        print(mcqs_text)

        save_txt(mcqs_text, f"generated_mcqs_{topic_key}.txt")
        save_pdf(mcqs_text, f"generated_mcqs_{topic_key}.pdf")

        # Parse MCQs
        quiz_questions = []
        for block in mcqs_text.split("## MCQ"):
            lines = [line.strip() for line in block.split("\n") if line.strip()]
            if not lines:
                continue

            question_line = "No question text provided"
            options = {}
            correct_match = ""

            for line in lines:
                if line.lower().startswith("question"):
                    question_line = re.sub(r"^question\s*:?\s*", "", line, flags=re.I).strip()
                m = re.match(r"^([A-D])\)\s*(.+)$", line, re.I)
                if m:
                    options[m.group(1).upper()] = m.group(2).strip()
                m = re.search(r"correct\s*answer\s*[:\-]?\s*([A-D])", line, re.I)
                if m:
                    correct_match = m.group(1).upper()

            if options:
                quiz_questions.append({
                    "question": question_line,
                    "options": options,
                    "correct": correct_match
                })

        if not quiz_questions:
            return "No MCQs generated. Try regenerating.", 500

        return render_template(
            "quiz.html",
            topic_name=topic_name,
            questions=quiz_questions,
            selected_domain=domain_name
        )

    elif request.method == "POST":
        score = 0
        total = int(request.form.get("total", 0))
        results = []

        for i in range(total):
            selected = request.form.get(f"q{i}", "").strip()
            correct = request.form.get(f"correct{i}", "").strip()
            question = request.form.get(f"question{i}", "").strip()

            results.append({
                "question_num": i + 1,
                "selected": selected or "(none)",
                "correct": correct or "(none)",
                "question": question
            })

            print(f"Q{i+1}: Selected = {selected or '(none)'} | Correct = {correct or '(none)'}")

            if selected and correct and selected.upper() == correct.upper():
                score += 1

        with get_db() as conn:
            prog = conn.execute(
                "SELECT * FROM progress WHERE username=? AND topic_key=?", (g.user, topic_key)
            ).fetchone()

            if prog is None:
                conn.execute(
                    "INSERT INTO progress (username, topic_key, quiz_completed) VALUES (?, ?, 1)",
                    (g.user, topic_key)
                )
                add_user_xp(g.user, 100, conn)   # ✅ reuse conn
            elif (prog["quiz_completed"] or 0) == 0:
                conn.execute(
                    "UPDATE progress SET quiz_completed=1 WHERE username=? AND topic_key=?",
                    (g.user, topic_key)
                )
                add_user_xp(g.user, 100, conn)   # ✅ reuse conn
            conn.commit()    

        return render_template(
            "result.html",
            score=score,
            total=total,
            topic_key=topic_key,
            results=results
        )



import google.generativeai as genai
from markupsafe import escape
import json

genai.configure(api_key='AIzaSyBfvijC3DuUVEH5EH3ZV3zZAcXpnnwK5b8')

# Function to call Gemini and get roadmap
import re
import json
import io
system_prompt = "You are a helpful study assistant. Always return structured JSON if possible."
from PIL import Image
def create_image_analysis(image_file, query):
    import io
    
    # Define generation config locally
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_output_tokens": 1024,
    }

    # Define safety settings locally
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    system_prompt = """
    You are an AI assistant that analyzes images.
    Provide structured JSON if possible, with keys in lowercase.
    Example:
    {
      "description": "this image shows a scatter plot",
      "details": ["axis labels are missing", "points clustered in top-right"],
      "suggestions": ["add labels", "consider color coding"]
    }
    """

    # Init model
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        safety_settings=safety_settings,
        generation_config=generation_config,
        system_instruction=system_prompt,
    )

    # Convert image file to bytes
    image_bytes = image_file.read()

    # Send image + query
    response = model.generate_content(
        [
            {"mime_type": "image/png", "data": image_bytes},
            query,
        ],
        stream=False,
    )

    print("Gemini raw response:", response.text)

    # Parse JSON safely
    try:
        data = json.loads(response.text)
    except json.JSONDecodeError:
        json_match = re.search(r"\{[\s\S]*\}", response.text)
        if json_match:
            data = json.loads(json_match.group())
        else:
            data = {"description": response.text}  # fallback

    return data
################################################################################
#----------------------------------------------------------------------------------------------------------------------------
def generate_mcqs(topic):
    system_prompt_mcq = """
    You are an AI agent creating 5 multiple choice questions (MCQs) to test knowledge on a given topic.
    Format output as a JSON list containing objects with "question" (string), "options" (list of strings), and "answer" (int index).
    Output only JSON.
    """
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "max_output_tokens": 1024,
        "response_mime_type": "application/json",
    }
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        safety_settings=safety_settings,
        generation_config=generation_config,
        system_instruction=system_prompt_mcq,
    )
    chat = model.start_chat(history=[])
    response = chat.send_message(f"Generate 5 MCQs on topic: {topic}", stream=False)

    try:
        mcqs = json.loads(response.text)
    except json.JSONDecodeError:
        json_match = re.search(r"\[.*\]", response.text, re.DOTALL)
        if json_match:
            mcqs = json.loads(json_match.group())
        else:
            raise ValueError("Failed to parse MCQs JSON.")
    return mcqs

def create_roadmap(topic, time, knowledge_level):
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
    }
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    system_prompt = """
    You are an AI agent who provides good personalized learning paths based on user input.
    Provide subtopics with descriptions and estimated time for each.
    Make sure all keys are lowercase.
    Output only JSON.
    Example:
    {
      "week 1": {
        "topic":"introduction to python",
        "subtopics":[
          {"subtopic":"getting started with python", "time":"10 minutes", "description":"learn hello world in python"},
          {"subtopic":"data types in python", "time":"1 hour", "description":"learn about int, string, boolean, array, dict and casting data types"}
        ]
      }
    }
    """

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        safety_settings=safety_settings,
        generation_config=generation_config,
        system_instruction=system_prompt,
    )

    chat_session = model.start_chat(history=[])

    response = chat_session.send_message(
        f"Suggest a roadmap for learning {topic} in {time}. "
        f"My knowledge level is {knowledge_level}. I can spend a total of 16 hours every week.",
        stream=False,
    )

    print("Gemini raw response:", response.text)

    try:
        data = json.loads(response.text)
    except json.JSONDecodeError:
        json_match = re.search(r"\{[\s\S]*\}", response.text)
        if json_match:
            data = json.loads(json_match.group())
        else:
            raise ValueError("Could not parse roadmap JSON.")

    def normalize(d):
        if isinstance(d, dict):
            return {str(k).lower(): normalize(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [normalize(i) for i in d]
        else:
            return d

    data = normalize(data)

    if isinstance(data, list):
        merged = {}
        for item in data:
            if isinstance(item, dict):
                for k, v in item.items():
                    lk = k.lower()
                    merged[lk] = v
        return merged
    return data

def determine_knowledge_level(score, total):
    ratio = score / total
    if ratio <= 0.2:
        return "beginner"
    elif ratio <= 0.6:
        return "intermediate"
    else:
        return "advanced"

@app.route("/roadmap", methods=["GET", "POST"])
def roadmap():
    if request.method == "POST":
        topic = request.form.get("topic")
        time = request.form.get("time")

        try:
            mcqs = generate_mcqs(topic)
        except Exception as e:
            return f"Error generating MCQs: {e}"

        session['mcqs'] = mcqs
        session['topic'] = topic
        session['time'] = time

        return redirect(url_for("roadmap_mcq"))

    return render_template("roadmap.html")


@app.route("/roadmap_mcq", methods=["GET", "POST"])
def roadmap_mcq():
    mcqs = session.get('mcqs')
    topic = session.get('topic')
    time = session.get('time')
    if not mcqs or not topic or not time:
        return redirect(url_for("roadmap"))

    if request.method == "POST":
        answers = []
        for i in range(len(mcqs)):
            ans = request.form.get(f"q{i}")
            if ans is None:
                answers.append(-1)
            else:
                answers.append(int(ans))

        score = 0
        for idx, mcq in enumerate(mcqs):
            if answers[idx] == mcq['answer']:
                score += 1

        level = determine_knowledge_level(score, len(mcqs))

        roadmap = create_roadmap(topic, time, level)

        display_roadmap = defaultdict(dict)
        for key, val in roadmap.items():
            display_roadmap[key]["topic"] = val.get("topic", "")
            display_roadmap[key]["description"] = val.get("description", "")
            display_roadmap[key]["activities"] = [st.get("subtopic", "") + f" ({st.get('time', '')})" for st in val.get("subtopics", [])]
            display_roadmap[key]["resources"] = val.get("resources", []) if val.get("resources") else []

        return render_template(
            "roadmap_display.html",
            roadmap=display_roadmap,
            topic=topic,
            time=time,
            level=level,
            score=score,
            total=len(mcqs)
        )

    return render_template("roadmap_mcq.html", mcqs=mcqs, topic=topic, time=time)
# ------------------- Routes -------------------

# ------------------- Helper: Image Analysis -------------------



# ------------------- Route: Image Analysis -------------------

@app.route("/analyze_image", methods=["GET", "POST"])
@login_required
def analyze_image():
    if request.method == "POST":
        image_file = request.files.get("image")

        if not image_file:
            return render_template("analyze_image.html", result="No image uploaded.")

        try:
            # Call helper just like roadmap
            analysis_data = create_image_analysis(
                image_file,
                "Analyze this study material image and extract key points, concepts, or possible questions."
            )
            result = json.dumps(analysis_data, indent=2)  # pretty print JSON
        except Exception as e:
            print("Error analyzing image:", e)
            result = "Error analyzing image."

        return render_template("analyze_image.html", result=result)

    return render_template("analyze_image.html", result=None)
API_URL = "https://jsearch.p.rapidapi.com/search"
HEADERS = {
    "x-rapidapi-key": "88d92b410dmsh51dba6e18185a6cp154d85jsnb8d4f0a4112e",  # replace with your key
    "x-rapidapi-host": "jsearch.p.rapidapi.com"
}

def fetch_jobs(query="software developer in India", page=1, num_pages=1):
    params = {"query": query, "page": str(page), "num_pages": str(num_pages)}
    try:
        response = requests.get(API_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()

        jobs = []
        if "data" in data:
            for job in data["data"]:
                jobs.append({
                    "title": job.get("job_title", "N/A"),
                    "company": job.get("employer_name", "N/A"),
                    "location": f"{job.get('job_city', '')}, {job.get('job_country', '')}",
                    "salary": f"{job.get('job_salary_currency','')} {job.get('job_min_salary')} - {job.get('job_max_salary')}" 
                               if job.get("job_min_salary") and job.get("job_max_salary") else "Not disclosed",
                    "link": job.get("job_apply_link", "#")
                })
        return jobs
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []
# def generate_interview_questions(topic):
#     try:
#         prompt = f"Generate 10 high-quality interview questions about {topic}. Return only the questions as a numbered list."
#         response = gemini_model.generate_content(prompt)
#         questions = [
#             q.split(". ", 1)[-1].strip()
#             for q in response.text.split("\n")
#             if q.strip() and any(c.isalpha() for c in q)
#         ]
#         return questions
#     except Exception as e:
#         print("Error generating questions:", e)
#         return []


# # Generate feedback using Gemini
# import re
# def generate_answer_feedback(question, user_answer):
#     prompt = f"""
#     Question: {question}
#     User's Answer: {user_answer}
#     Give:
#     1. Correct answer (label it 'Correct answer:')
#     2. Feedback on user's answer (label it 'Feedback on user's answer:')
#     3. State Correct or Incorrect (label it 'Correct or Incorrect:')
#     """
#     response = gemini_model.generate_content(prompt)
#     text = response.text

#     correct_answer = re.search(r"Correct answer:\s*(.*?)(?=Feedback|$)", text, re.S)
#     feedback = re.search(r"Feedback on user's answer:\s*(.*?)(?=Correct or Incorrect|$)", text, re.S)
#     verdict = re.search(r"Correct or Incorrect:\s*(.*)", text)

#     return {
#         "correct_answer": correct_answer.group(1).strip() if correct_answer else "",
#         "feedback": feedback.group(1).strip() if feedback else "",
#         "verdict": verdict.group(1).strip() if verdict else ""
#     }


# @app.route('/ai_interview', methods=['GET', 'POST'])
# def ai_interview():
#     if 'questions' not in session:
#         session['questions'] = []
#         session['current'] = 0
#         session['score'] = 0
#         session['answers'] = []

#     step = "start"
#     question = None
#     answer = None
#     progress = None
#     total = len(session['questions'])

#     if request.method == 'POST':
#         if 'topic' in request.form:
#             topic = request.form['topic']
#             questions = generate_interview_questions(topic)
#             session['questions'] = questions
#             session['current'] = 0
#             session['score'] = 0
#             session['answers'] = []
#             step = "ask"
#             question = questions[0]
#             progress = f"1 / {len(questions)}"

#         elif 'user_answer' in request.form:
#             user_answer = request.form['user_answer']
#             current_index = session['current']
#             question = session['questions'][current_index]
#             answer = generate_answer_feedback(question, user_answer)

#             # Score update
#             if "Correct" in answer['verdict']:
#                 session['score'] += 1

#             session['answers'].append(answer)
#             step = "feedback"
#             progress = f"{current_index + 1} / {len(session['questions'])}"

#         elif 'next' in request.form:
#             session['current'] += 1
#             if session['current'] >= len(session['questions']):
#                 step = "done"
#             else:
#                 step = "ask"
#                 question = session['questions'][session['current']]
#                 progress = f"{session['current'] + 1} / {len(session['questions'])}"

#     return render_template('ai_interview.html',
#                            step=step,
#                            question=question,
#                            progress=progress,
#                            answer=answer,
#                            score=session['score'],
#                            total=len(session['questions']))

def generate_interview_questions(topic):
    try:
        prompt = f"Generate 10 high-quality interview questions about {topic}. Return only the questions as a numbered list."
        response = gemini_model.generate_content(prompt)
        questions = [
            q.split(". ", 1)[-1].strip()
            for q in response.text.split("\n")
            if q.strip() and any(c.isalpha() for c in q)
        ]
        return questions
    except Exception as e:
        print("Error generating questions:", e)
        return []


# Generate feedback using Gemini
import re
def generate_answer_feedback(question, user_answer):
    prompt = f"""
    Question: {question}
    User's Answer: {user_answer}
    Give:
    1. Correct answer (label it 'Correct answer:')
    2. Feedback on user's answer (label it 'Feedback on user's answer:')
    3. State Correct or Incorrect (label it 'Correct or Incorrect:')
    """
    response = gemini_model.generate_content(prompt)
    text = response.text

    correct_answer = re.search(r"Correct answer:\s*(.*?)(?=Feedback|$)", text, re.S)
    feedback = re.search(r"Feedback on user's answer:\s*(.*?)(?=Correct or Incorrect|$)", text, re.S)
    verdict = re.search(r"Correct or Incorrect:\s*(.*)", text)

    return {
        "correct_answer": correct_answer.group(1).strip() if correct_answer else "",
        "feedback": feedback.group(1).strip() if feedback else "",
        "verdict": verdict.group(1).strip() if verdict else ""
    }

@app.route('/ai_interview', methods=['GET', 'POST'])
def ai_interview():
    if 'questions' not in session:
        session['questions'] = []
        session['current'] = 0
        session['score'] = 0
        session['answers'] = []

    step = "start"
    question = None
    answer = None
    progress = None
    total = len(session['questions'])

    if request.method == 'POST':
        # Step 1: Start interview
        if 'topic' in request.form:
            topic = request.form['topic']
            questions = generate_interview_questions(topic)
            session['questions'] = questions
            session['current'] = 0
            session['score'] = 0
            session['answers'] = []

            if questions:  # Only access if not empty
                step = "ask"
                question = questions[0]
                progress = f"1 / {len(questions)}"
            else:
                step = "start"

        # Step 2: Submit answer
        elif 'user_answer' in request.form:
            current_index = session['current']
            if current_index < len(session['questions']):
                question = session['questions'][current_index]
                user_answer = request.form['user_answer']
                answer = generate_answer_feedback(question, user_answer)

                # Score update
                if "Correct" in answer['verdict']:
                    session['score'] += 1

                session['answers'].append(answer)
                step = "feedback"
                progress = f"{current_index + 1} / {len(session['questions'])}"
            else:
                # Safety fallback
                step = "done"

        # Step 3: Next question
        elif 'next' in request.form:
            session['current'] += 1
            if session['current'] < len(session['questions']):
                step = "ask"
                question = session['questions'][session['current']]
                progress = f"{session['current'] + 1} / {len(session['questions'])}"
            else:
                step = "done"

    return render_template('ai_interview.html',
                           step=step,
                           question=question,
                           progress=progress,
                           answer=answer,
                           score=session.get('score', 0),
                           total=len(session['questions']))

@app.route("/news", methods=["GET", "POST"])
@login_required
def news():
    category = "Software Developer"  # Default
    if request.method == "POST":
        category = request.form.get("category", category)

    jobs = fetch_jobs(f"{category} jobs in India", page=1, num_pages=1)
    internships = fetch_jobs(f"{category} internships in India", page=1, num_pages=1)

    return render_template("news.html", jobs=jobs, internships=internships, selected_category=category)

@app.route("/leaderboard")
@login_required
def leaderboard():
    conn = get_db()  # ✅ get connection
    try:
        # Fetch top 10 users
        cur = conn.execute("""
            SELECT username, xp_points 
            FROM users 
            ORDER BY xp_points DESC 
            LIMIT 10
        """)
        leaderboard_data = cur.fetchall()
        print(leaderboard_data)  # check data

        # Current user's global rank
        username = session["user"]
        rank_row = conn.execute("""
            SELECT COUNT(*) + 1 AS rank 
            FROM users 
            WHERE xp_points > (SELECT xp_points FROM users WHERE username = ?)
        """, (username,)).fetchone()
        user_rank = rank_row["rank"]

        # Current user's XP
        user_data = conn.execute("SELECT xp_points FROM users WHERE username = ?", (username,)).fetchone()
        user_xp = user_data["xp_points"]
    finally:
        conn.close()  # always close connection

    return render_template(
        "leaderboard.html",
        leaderboard=leaderboard_data,
        user_rank=user_rank,
        user_xp=user_xp
    )


@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
	message = None
	if request.method == "POST":
		# In real apps, send email or store the message here.
		message = "Thank you for your message! We'll get back to you soon."
	return render_template("contact.html", message=message)        
#------------------------THE END--------------------------------
def parse_mcq_file():
    with open("mcq.txt", "r") as f:
        content = f.read()

    blocks = content.strip().split("## MCQ")
    questions = []

    for block in blocks[1:]:
        q_data = {}
        question_match = re.search(r"Question:\s*(.*)", block)
        options_match = re.findall(r"([A-D])\)\s*(.*)", block)
        answer_match = re.search(r"Correct Answer:\s*([A-D])", block)

        if question_match and options_match and answer_match:
            q_data["question"] = question_match.group(1)
            q_data["options"] = {opt: text for opt, text in options_match}
            q_data["answer"] = answer_match.group(1)
            questions.append(q_data)

    return questions
last_score=None
# -------- Route to send questions --------
@app.route("/questions")
def get_questions():
    return jsonify(parse_mcq_file())

# -------- Route to submit score --------
@app.route("/submit_score", methods=["GET"])
def submit_score():
    global last_score
    
    # Read score and total from query params
    score = request.args.get("score", type=int)
    total = request.args.get("total", type=int)

    if score is None or total is None:
        return "Missing score or total", 400

    # Store score in JSON file
    score_file = "scores.json"
    if os.path.exists(score_file):
        with open(score_file, "r") as f:
            scores = json.load(f)
    else:
        scores = []

    scores.append({"score": score, "total": total})
    with open(score_file, "w") as f:
        json.dump(scores, f, indent=4)

    last_score = score
    print(f"User scored {score} out of {total}")
    print("=== LEADERBOARD2 ROUTE STARTED ===")
    
    conn = None
    try:
        conn = get_db()
        username = session.get("user")
        print(f"Username from session: {username}")
        print(f"Last score: {last_score}")
        
        if not username:
            print("ERROR: No username in session")
            return "No username in session", 400
        
        conn.execute("INSERT INTO extra (name, score) VALUES (?, ?)", (username, last_score))
        conn.commit()
        print("Insert successful")
        
        cur = conn.execute("""
            SELECT username, xp_points 
            FROM users 
            ORDER BY xp_points DESC 
            LIMIT 10
        """)
        leaderboard_data = cur.fetchall()
        
        rank_row = conn.execute("""
            SELECT COUNT(*) + 1 AS rank 
            FROM extra
            WHERE score > (SELECT score FROM extra WHERE name = ?)
        """, (username,)).fetchone()
        
        user_rank = rank_row["rank"] if rank_row else 1
        user_data = conn.execute("SELECT score FROM extra WHERE name = ?", (username,)).fetchone()
        user_xp = user_data["score"] if user_data else last_score
        
        return render_template(
            "leaderboard2.html",
            leaderboard2=leaderboard_data,
            user_rank=user_rank,
            user_xp=user_xp
        )
        
    except Exception as e:
        print(f"ERROR in leaderboard2 route: {e}")
        import traceback
        traceback.print_exc()
        return f"Database error: {e}", 500
        
    finally:
        if conn:
            conn.close()
            print("Database connection closed")

    
# -------- Contest route --------
@app.route("/contest")
def contest():
    return render_template("extra2.html")
@app.route("/extra")
def extra():
    return render_template("extra.html")
#-------------------------------AMIT-------------------------------

    

# ---------------- Run Application ----------------
if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)


 