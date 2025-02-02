# 1️⃣ Base Image
FROM python:3.13-slim

# 2️⃣ Set the working directory
WORKDIR /app

# 3️⃣ Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4️⃣ Copy the rest of the code
COPY . .

# 5️⃣ Expose the port Render will use
EXPOSE 10000

# 6️⃣ Start the FastAPI server using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
