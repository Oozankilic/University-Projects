/**
 *@file part_b_server.c
 *@author Ozan Kılıç 
 *
 *@brief This is the client side of the part b. This part of the project takes arguments from the terminal. Then takes stdin inputs from terminal. With these values, calls part_b_prog_1
 * function, which is created by rpcgen lib. That function makes RPC with given values. Then writes the result to the file as given in arguments.
 */

#include "part_b.h"
#include <ctype.h>

// this method calls remote call procedure. Details are in the method body
void
part_b_prog_1(char *host, int x, int y, char path[1000], char *outputPath)
{
	CLIENT *clnt;
	char * *result_1;
	numbers  part_b_1_arg;

#ifndef	DEBUG
	clnt = clnt_create (host, PART_B_PROG, PART_B_VERS, "udp");
	if (clnt == NULL) {
		clnt_pcreateerror (host);
		exit (1);
	}
#endif	/* DEBUG */
	// below three lines sends x and y values to arg.a and arg.b and path of blackbox file to arg.path
	part_b_1_arg.a = x;
	part_b_1_arg.b = y;
	strcpy(part_b_1_arg.path,path);

	result_1 = part_b_1(&part_b_1_arg, clnt);
	if (result_1 == (char **) NULL) {
		clnt_perror (clnt, "call failed");
	}else{
		
		// Opens the file and writes the result to the file given as argument
		FILE *fp;
		fp = fopen(outputPath, "a");

		// looks if the return value is Succcess of Fail, then writes down the result
		fprintf(fp,"%s", *result_1);

		//file is closed 
		fclose(fp); 
	}
#ifndef	DEBUG
	clnt_destroy (clnt);
#endif	 /* DEBUG */
}


// client main takes arguments and stdin values from terminal and calls rpc via part_b_prog_1 method
int
main (int argc, char *argv[])
{
	char *host;
	char *blackboxPath;	
	char *outputPath;
	int x, y;
	 
	if (argc < 2) {
		printf ("usage: %s server_host\n", argv[0]);
		exit (1);
	}
	host = argv[3];
	blackboxPath = argv[1];
	outputPath = argv[2];
	scanf("%d %d", &x, &y);
	part_b_prog_1 (host, x, y, blackboxPath, outputPath);
exit (0);
}
