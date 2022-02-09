/**
 *@file part_a.c
 *@author Ozan Kılıç 
 *
 *@brief This part of the project runs blackbox with creating a child process. While doing this, creates pipes between
 * processes and changes child's stdin, stdout, stderr structures. At the end parent writes down the output to the file
 * part_a_output.txt
 */


#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <string.h>
#include <ctype.h>
#include<sys/wait.h>

int main(int argc, char *argv[]){

	// toChild and toParent are created for piping, buffers are for saving data between parent and the child processes.
	// pid_t is to create subprocess and pid is to take procesid.
	int toChild[2], toParent[2];
	char buffer[1000];
	pid_t pid;
	char w_buf[10000], r_buf[10000], er_buf[10000];


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
		int nbytes;
		int x, y;

		// closing unnecessary pipe sides
		close(toChild[0]);
		close(toParent[1]);

		// takes input integers
		scanf("%d %d", &x, &y);

		//prints integers to the write buffer to send to child process and writes them down to child pipe
		sprintf(w_buf, "%d %d", x, y);
		write(toChild[1], w_buf, sizeof(buffer));

		// wait for the response of the child and gets the result
		nbytes = read(toParent[0], r_buf, sizeof(r_buf));
		int status;
		int returned;
		wait(&status);
		if (WIFEXITED(status)){
			returned = WEXITSTATUS(status);
		}
		char* outputPath = argv[2];
		// write the output on part_a_output.txt file
		FILE *fp;
		fp = fopen(outputPath, "a");

		// looks if the return value is Succcess of Fail, then writes down the result
		if(returned == 0){
			fprintf(fp,"SUCCESS: \n%s", r_buf);
		}
		if(returned == 1){
			fprintf(fp,"FAIL: \n%s", r_buf);
		}

		//file is closed 
		fclose(fp); 
	}


	//child process
	if(pid == 0){

		// stdin, stdout and stderr values are directed to parent's output and input
		dup2(toChild[0], STDIN_FILENO);
		dup2(toParent[1], STDOUT_FILENO);
		dup2(toParent[1], STDOUT_FILENO);
		dup2(toParent[1], STDERR_FILENO);

		// unnecessary pipes are closed
		close(toChild[1]);
		close(toParent[0]);
		close(toChild[0]);
		close(toParent[1]);

		// blackbox file is taken via makefile as char b. execl runs the blackbox without parameters. scanf waits
		// for input from the parent and blackbox takes them because in that time blackbox is running
		int x, y;
		char* b = argv[1];
		execl(b, b, x, y, NULL);
		scanf("%d %d", &x, &y);

	}
}

// as conclusion, program runs the blackbox in child process with given inputs and returns the end value to parent. parent
// writes them down to the ouput file.