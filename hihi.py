#!/usr/bin/python3
import sys
print("Environment: " + sys.argv[1])
print("Queue Name: " + sys.argv[2])
print("Dead Letter Queue Name: " + sys.argv[3])
print("Max Receive Count: " + sys.argv[4])
print("LOB: " + sys.argv[5])
print("REF_ID: " + sys.argv[6])
print("Application Name: " + sys.argv[7])
print("SNS Topic Name: " + sys.argv[8])
print("SNS Subscription Required: " + sys.argv[9])

# Print the number of arguments
print(len(sys.argv))