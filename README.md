# mini_project
This project’s main purpose is to develop a RESTful Application Program Interface (API) based on knowledge acquired from this module’s labs. 
This particular application allows clients to access content (ten random jokes) previously stored in a database and also to remotely add, update and delete new resources. The implemented methods for that were GET, POST, PUT and DELETE.
 
For this application, a t2.medium instance was used. The first step after that was to set up a Cassandra node inside a docker container and pull the latest Cassandra Docker Image using the following command:
sudo docker pull cassandra:latest

The next step was to run a Cassandra instance 
sudo docker run –name cassandra-cloud -p 9042:9042 -d cassandra:latest 

Then it was possible to interact with it via cqlsh using CQL
sudo docker exec -it cassandra-cloud cqlsh
Inside of this terminal was created a table with the necessary parameters for this application (id and joke)

Finally, it was possible to pull data from the Cassandra database into a flask web client by creating requirements.txt, Dockerfile and app.py, build the image and run it as a service using the commands:
sudo docker build . –tag=cassandrarest:v1
sudo docker run -p 80:80 cassandrarest:v1

After that, an authentication service was created where clients can register, login and logout of the page and that detects errors such as wrong username/password. 
