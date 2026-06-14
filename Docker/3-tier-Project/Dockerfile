FROM ubuntu
WORKDIR /mydir
RUN  apt update -y && apt install -y curl && curl -sL https://deb.nodesource.com/setup_16.x | bash && apt install -y nodejs
COPY package.json .
RUN npm install
COPY . .
RUN npm run build
RUN npm install -g serve
EXPOSE 5001
ENTRYPOINT ["serve","-s","-l","5001","build"]
