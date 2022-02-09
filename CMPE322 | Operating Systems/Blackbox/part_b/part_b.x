struct numbers{
	char path[1000];
	int a;
	int b;
};


program PART_B_PROG{
	version PART_B_VERS{
		string part_b(numbers) = 1;
	}=1;
}=0x56242897;