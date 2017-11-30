#include "storage.h"
#include "num.h"

#define MAXITEMS 4096
#define MAXNODES 4096

typedef struct 
{
	char key[32];
	char value[32];
} slot;

typedef struct
{
	uint16 trans[26];
	uint16 value;
} node;

node nodes[MAXNODES];
slot slots[MAXITEMS];
uint64 items_count;
uint64 next_node;

void init_storage()
{
	items_count = 0;
	next_node = 1;
	memzero(nodes, sizeof(nodes));
}

uint64 allocate_node()
{
	uint64 nd = next_node;
	next_node++;
	if (next_node >= MAXNODES)
		return 0;
	return nd;
}

uint16 add_item(const slot *item)
{
	// TODO handle overflow
	slots[items_count + 1] = *item;
	return ++items_count;
}

void copy_value(const void *src, void *dest)
{
	((uint64 *)dest)[0] = ((uint64 *)src)[0];
	((uint64 *)dest)[1] = ((uint64 *)src)[1];
	((uint64 *)dest)[2] = ((uint64 *)src)[2];
	((uint64 *)dest)[3] = ((uint64 *)src)[3];
}

char * store_item(const char *key, char *value)
{
	if (!key || !value)
		return 0;
	slot item;
	copy_value(value, item.value);
	if (!name_flag(key, item.key))
		return 0;

	uint64 current = 0;

	for (key = item.key; *key && key < item.value; key++)
	{
		uint64 n = *key - 'A';
		if (n >= 26)
			return 0;
		if (!nodes[current].trans[n])
		{
			uint64 nd = allocate_node();
			if (!nd)
				return 0;
			nodes[current].trans[n] = nd;
		}
		current = nodes[current].trans[n];
	}

	if (nodes[current].value)
		return 0;

	nodes[current].value = add_item(&item);

	return value;
}

char * load_item(const char *key, char *buffer)
{
	if (!key || !buffer)
		return 0;

	uint64 current = 0;

	while (*key)
	{
		uint64 n = *key - 'A';
		if (n >= 26)
			return 0;
		if (!nodes[current].trans[n])
			return 0;
		current = nodes[current].trans[n];
		key++;
	}

	if (!nodes[current].value)
		return 0;

	copy_value(slots[nodes[current].value].value, buffer);
	buffer[32] = 0; 

	return buffer;
}

char * list_items(uint64 skip, uint64 take, char *buffer, uint64 length)
{
	if (!buffer)
		return 0;

	if ((skip + take) * 33 > length)
		return 0;

	buffer[0] = 0;

	uint64 i;
	for (i = skip; i < skip + take; i++)
	{
		if (i >= items_count)
			break;
		strncat(buffer, slots[i + 1].key, 32);
		strcat(buffer, "\n");
	}

	return buffer;
}

#define CSPIRITS 30
#define MAXRECIPE 32
char *spirits[] = {
"Ale",
"Porter",
"Stout",
"Lager",
"Cider",
"Mead",
"Sake",
"Wine",
"Port",
"Sherry",
"Vermouth",
"Vinsanto",
"Sangria",
"Champagne",
"Absinthe",
"Brandy",
"Armagnac",
"Cognac",
"Schnapps",
"Gin",
"Horilka",
"Metaxa",
"Rakia",
"Rum",
"Shochu",
"Soju",
"Tequila",
"Vodka",
"Bourbon",
"Whiskey"
};

char * encode_flag(const char *recipe, char *buffer)
{
	if (!recipe || !buffer)
		return 0;

	uint192 n = expand(0);

	char buf[32];
	buf[0] = 0;
	char *bptr = buf;
	while (*recipe && bptr < buf + sizeof(buf))
	{
		char c = *recipe;
		if (c == ',' || !recipe[1])
		{
			if (!recipe[1])
			{
				*bptr = *recipe;
				bptr++;
			}
			*bptr = 0;
			uint64 i;
			for (i = 0; i < CSPIRITS; i++)
			{
				if (!strcmp(buf, spirits[i]))
					break;
			}

			if (i >= CSPIRITS)
				return 0;

			n = multiply(n, MAXRECIPE);
			n = add(n, i);

			buf[0] = 0;
			bptr = buf;
		}
		else
		{
			*bptr = *recipe;
			bptr++;
		}
		recipe++;
	}
	
	buffer[32] = 0;
	buffer[31] = '=';
	buffer += 30;
	uint64 length = 0;
	while (!is_zero(n) && length < 31)
	{
		uint32 rem;
		n = divmod(n, 36, &rem);
		*buffer = rem > 9 ? 'A' + rem - 10 : '0' + rem;
		buffer--;
		length++;
	}

	while (length < 31)
	{
		*buffer = '0';
		buffer--;
		length++;
	}

	return buffer + 1;
}

char * hash_flag(const char *flag, char *buffer)
{
	if (!flag || !buffer)
		return 0;
	char *bptr = buffer;
	while (*flag)
	{
		*bptr = *flag;
		flag++;
		bptr++;
	}
	*bptr = 0;
	return buffer;
}

char * name_flag(const char *flag, char *buffer)
{
	if (!flag || !buffer)
		return 0;
	uint64 length = 0;
	while (*flag)
	{
		char c = *flag;
		flag++;
		if (c < 'A' || c > 'Z')
			continue;
		*buffer = c;
		buffer++;
		length++;
	}

	if (!length)
		return 0;

	*buffer = 0;

	return buffer - length;
}