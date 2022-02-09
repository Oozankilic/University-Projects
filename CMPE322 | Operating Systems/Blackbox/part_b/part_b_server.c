/**
 *@file part_b_server.c
 *@author Ozan Kılıç 
 *
 *@brief This is the servers side of the part b. This part of the project runs blackbox with creating a child process. While doing this, creates pipes between
 * processes and changes child's stdin, stdout, stderr structures. At the end parent writes down the output according to the return value of child process. At 
 * the end returns result string to the client process
 */

#include "part_b.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <string.h>
#include<sys/wait.h>

char **
part_b_1_svc(numbers *argp, struct svc_req *rqstp)
{
	// result saves the return value and at the end returns it
	static char * result;
	
	// toChild and toParent are created for piping, buffers are for saving data between parent and the child processes.
	// pid_t is to create subprocess and pid is to take procesid.

	int toChild[2], toParent[2];
	pid_t pid;
	char w_buf[64000], r_buf[64000];

	//pipes are created and unused sides closed for a proper communication channel.

	pipe(toChild);
	pipe(toParent);

	// fork creates child process
	pid = fork();

	//fork control
	if(pid == -1){
		fprintf(stderr, "forking failed.");
		exit(-1);
	}

	//parent process
	if(pid > 0 ){
		int x, y;
		char return_buf[64000];
		x = argp->a;
		y = argp->b;
		int nbytes;

		// closing unnecessary pipe sides
		close(toChild[0]);
		close(toParent[1]);

		// prints integers to the write buffer to send to child process and writes them down to child pipe
		sprintf(w_buf, "%d %d", x, y);
		write(toChild[1], w_buf, sizeof(r_buf));
		
		// below part waits for the child process to end. And takes it status from wait function, then takes the return falue of the child process as int returned.
		int status;
		int returned;
		wait(&status);
		if (WIFEXITED(status)){
			returned = WEXITSTATUS(status);
		}

		// reads the values coming from the child process and writes them to r_buf buffer
		nbytes = read(toParent[0], r_buf, sizeof(r_buf));
		
		// checks the return value of the child process and according to the result, creates success and fail message to be sent to client program
		if(returned == 0){
			sprintf(return_buf,"SUCCESS: \n%s", r_buf);
		}
		if(returned == 1){
			sprintf(return_buf,"FAIL: \n%s", r_buf);
		}

		// returns the result message to client
		result = return_buf;
		return &result;
		
	}


	//child
	if(pid == 0){

		// stdin, stdout and stderr values are directed to parent's output and input
		dup2(toChild[0], STDIN_FILENO);
		dup2(toParent[1], STDOUT_FILENO);
		dup2(toParent[1], STDERR_FILENO);

		// unnecessary pipes are closed
		close(toChild[1]);
		close(toParent[0]);
		close(toChild[0]);
		close(toParent[1]);

		// blackbox file is taken via makefile as char path. execl runs the blackbox without parameters. scanf waits
		// for input from the parent and blackbox takes them because in that time blackbox is running
		char path[1000];
		strcpy(path, argp->path);
		int z, t;
		execl(path, path, z, t, NULL);
		scanf("%d %d", &z, &t);

	}
}
