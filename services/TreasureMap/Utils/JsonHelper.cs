﻿using System;
using System.Globalization;
using System.IO;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;
using System.Text;
using System.Threading.Tasks;
using System.Xml;

namespace TreasureMap.Utils
{
	public static class JsonHelper
	{
		public static async Task<T> TryParseJsonAsync<T>(Stream stream)
		{
			try
			{
				using (var reader = new StreamReader(stream, Encoding.UTF8, false, 1024, true))
				{
					var record = await reader.ReadToEndAsync().ConfigureAwait(false);
					return ParseJson<T>(record);
				}
			} catch (Exception) { return default(T); }
		}

		public static T TryParseJson<T>(string record)
		{
			try { return ParseJson<T>(record); } catch(Exception) { return default(T); }
		}

		public static T TryParseJson<T>(Stream stream)
		{
			try { return ParseJson<T>(stream); } catch (Exception) { return default(T); }
		}

		public static T ParseJson<T>(string record)
		{
			return ParseJson<T>(Encoding.UTF8.GetBytes(record));
		}

		public static T ParseJson<T>(byte[] record)
		{
			return ParseJson<T>(record, 0, record.Length);
		}

		public static T ParseJson<T>(byte[] record, int offset, int length)
		{
			var reader = JsonReaderWriterFactory.CreateJsonReader(record, offset, length, XmlDictionaryReaderQuotas.Max);
			return (T)new DataContractJsonSerializer(typeof(T)).ReadObject(reader);
		}

		public static T ParseJson<T>(Stream stream)
		{
			var reader = JsonReaderWriterFactory.CreateJsonReader(stream, XmlDictionaryReaderQuotas.Max);
			return (T)new DataContractJsonSerializer(typeof(T)).ReadObject(reader);
		}

		public static string ToJsonString<T>(this T obj, bool runtime = true)
		{
			return Encoding.UTF8.GetString(obj.ToJson(runtime));
		}

		public static byte[] ToJson<T>(this T obj, bool runtime = true)
		{
			using(var stream = new MemoryStream())
			{
				obj.ToJson(stream, runtime);
				return stream.ToArray();
			}
		}

		public static void ToJson<T>(this T obj, Stream stream, bool runtime = true)
		{
			using(var writer = JsonReaderWriterFactory.CreateJsonWriter(stream, Encoding.UTF8, false))
				new DataContractJsonSerializer(runtime ? obj.TryGetRuntimeType() : typeof(T), Settings).WriteObject(writer, obj);
		}

		public static Type TryGetRuntimeType<T>(this T obj)
		{
			return Equals(obj, null) ? typeof(T) : obj.GetType();
		}

		private static readonly DataContractJsonSerializerSettings Settings = new DataContractJsonSerializerSettings { UseSimpleDictionaryFormat = true, SerializeReadOnlyTypes = true, DateTimeFormat = new DateTimeFormat("s", CultureInfo.InvariantCulture) };
	}
}