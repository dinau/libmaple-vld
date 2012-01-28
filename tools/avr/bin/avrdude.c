/*
#
# 2011/11 Modified by audin.
# 2011/09, Created by audin.
# http://avr.paslog.jp
#
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char cmd[512];
char arg_str[512];

int main(int argc,char **argv )
{
	FILE *fp;
	for( int i = 1; i < argc; i++ ) {
		strcat( arg_str, " " );
		strcat( arg_str, argv[ i ] );
	}
	printf("\nPlaceholder FAKE Avrdude is being invoked...\n");
	fflush( stdout );

	fp = fopen( "fwriter.exe" , "r" );
	if( fp != NULL ){
		strcpy( cmd, "fwriter.exe" );
	}
	else{
		fp = fopen( "fwriter.py" , "r" );
		if( fp == NULL ){
			puts( "\n--- fwriter.py is not found !----");
			return 1;
		}
		strcpy( cmd, "python fwriter.py" );
	}
	fclose( fp );
	strcat( cmd, arg_str );
	system( cmd );
	return 0;
}

