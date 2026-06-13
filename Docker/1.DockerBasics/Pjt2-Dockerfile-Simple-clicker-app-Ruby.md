Simple Cliker app 
- [Repo Link](https://github.com/docker-hy/material-applications/tree/main/rails-example-project(opens in a new tab))
---
README.md  ( follow the project repo above for all the code and ohter files)  

Installation
 Make sure you have a JavaScript runtime such as node installed.

Prerequisites
 Install ruby version 3.1.0.  

 Install the correct version of bundler with gem install bundler:2.3.3  

 Run bundle install to install all dependencies specified in the Gemfile  

- For development version  
 Run migrations with -->  
   > rails db:migrate    

  Run  to start the project in development mode  
   > rails s  

For production version  
 -  Run migrations with rails db:migrate RAILS_ENV=production  

 - Precompile your assets with rake assets:precompile  

  Run rails s -e production to start the project in production mode  

(To get error output use RAILS_LOG_TO_STDOUT=true rails s -e production)   

The application by default runs in port 3000
---
### Solution: Creating Dockerfile

```Dockerfile
FROM ruby:3.1.0

WORKDIR /usr/src/app

EXPOSE 3000

RUN gem install bundler:2.3.3

COPY Gemfile* ./
  
RUN bundle install
 
# Copy all of the source code
COPY . .
 
# We pick the production mode since we have no intention of developing the software inside the container.
# Run database migrations by following instructions from README
 
RUN rails db:migrate RAILS_ENV=production
 
# Precompile assets by following instructions from README
 
RUN rake assets:precompile

# And finally the command to run the application
CMD ["rails", "s", "-e", "production"]
```
## Build and Run
```
docker build . -t rails-project && docker run -p 3000:3000 rails-project
```
Once application Started,Check on browser
```
http://0.0.0.0:3000
```
Description:
- FROM a Ruby version, 
- EXPOSE 3000 was told at the bottom of the README and 
- WORKDIR /usr/src/app is the convention.
- COPY will copy both files Gemfile and Gemfile.lock to the current directory. 
- finally, we copy the project and follow the instructions in the README:
