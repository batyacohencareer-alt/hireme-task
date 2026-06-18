# GitHub AI Evaluator 🚀

A Full-Stack application that analyzes GitHub user profiles using Artificial Intelligence (Gemini API). The system takes a GitHub username or profile link, fetches the user's public repositories, reads their `README.md` files, and returns a smart AI assessment of the project's complexity, code quality, and clarity.
<img width="1129" height="1008" alt="image" src="https://github.com/user-attachments/assets/b5acc69c-a9d5-427a-8aec-de76ac40beb3" />


## 🛠️ Technologies & Stack
* **Frontend:** React, Vite, Tailwind CSS, Lucide Icons
* **Backend:** Python, FastAPI
* **AI & Integration:** Google Gemini API (AI Studio), GitHub API

## 🧠 My Approach to AI (AI-Native Workflow)
In this project, I aimed to use AI not just as a product feature, but as a full partner in the development process:
* **Gemini Web Interface:** Used for architectural brainstorming, logic planning, and solving complex bugs.
* **Gemini VS Code Agent:** Served as an in-editor Copilot for writing boilerplate code, generating functions, and quick debugging.
* **Google AI Studio (API):** The core engine powering the repository evaluations.

## 🚧 Core Challenge & Architecture Decisions
**The Challenge:** Handling Google Gemini's Free Tier Rate Limits (`429 RESOURCE_EXHAUSTED` errors). Initially, sending multiple repositories to the API simultaneously caused the server to crash or return errors due to quota limits.

**The Solution:** Instead of taking the easy route (upgrading to a paid tier), I solved this at the architecture level to ensure a resilient application:
1. **Smart Batching:** I refactored the logic to combine up to 5 repositories into a single API prompt. I specifically limited the batch size to 5 to maintain the quality of the LLM's responses, preventing context overload and AI "hallucinations" or shallow answers.
2. **Retry & Delay Mechanism:** Added a fallback mechanism with a 3-second delay (`asyncio.sleep`) between retries to ensure server stability under heavy load.
3. **Graceful Error Handling:** Handled edge cases seamlessly on the frontend (e.g., displaying a friendly UI state for a `404 User Not Found` instead of crashing, and handling repos without a README).

<img width="1129" height="1008" alt="image" src="https://github.com/user-attachments/assets/1c8c8544-bd62-4e02-b080-15aa2ed18c30" />

<img width="438" height="191" alt="image" src="https://github.com/user-attachments/assets/e7541a64-846f-4549-a621-522715dd18c3" />



## 🔮 Future Work
If I had another week to work on this project, I would add:
* **Resume-Ready Export:** A feature designed for candidates and recruiters, allowing users to export project evaluations into a polished, copy-paste format ready for CVs (highlighting key technologies and project impact).
* **Caching & Database:** Storing previous evaluation results in a database to save API calls and reduce wait times.
* **SaaS UI/UX:** Elevating the frontend design and user experience to a full SaaS product level.
* **Deep Code Analysis:** Expanding the API integration to analyze actual source code files in the repositories, rather than just the READMEs.

## 💻 Setup & Installation Instructions

**Prerequisites:**
* Node.js installed
* Python 3.x installed

### Backend Setup
1. Open a terminal and navigate to the backend folder:
   ```bash
   cd backend
