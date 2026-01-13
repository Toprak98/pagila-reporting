### AI Tool Used
ChatGPT

### Main Prompts
- Create a Streamlit app that connects to a PostgreSQL Pagila Data Warehouse and shows rentals by film category as a bar chart and rental trends over time as a line chart
- Fix Windows-related issues with pip, streamlit, and PostgreSQL connections
- Improve error handling and database defaults
- Improve the readability and layout of the charts

### What Worked Well
- ChatGPT was helpful for creating an initial structure of the Streamlit application
- Using the view `vw_rental_analysis` simplified SQL queries and reporting logic
- AI assistance was useful for resolving technical issues and improving chart readability

### Challenges
- At the beginning, ChatGPT assumed an incorrect database name and connected to the wrong database by default. This had to be identified and corrected manually (`pagila_dwh` instead of `pagila`)
- Environment and Path issues on Windows required several iterations and manual testing
- A key challenge was formulating very precise prompts, as the AI does not proactively ask follow-up questions and relies strictly on the given input
- Several AI-generated suggestions had to be reviewed and adjusted to match the actual database setup and reporting requirements