using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using PirateCoin.Utils;

namespace BlackMarket
{
	internal class StateManager
	{
		public StateManager(string stateFilepath)
		{
			if(File.Exists(stateFilepath))
				Load(stateFilepath);
			stateWriter = new StreamWriter(stateFilepath, true) { AutoFlush = true };
		}

		public void Insert(FlagData flagData)
		{
			stateWriter.WriteLine(flagData.ToJsonString());
			InsertInternal(flagData);
		}



		public List<FlagData> FindByContractAddr(string contractAddr)
		{
			if(!dict.TryGetValue(contractAddr, out var set))
				return null;
			lock(set)
				return set.ToList();
		}

		private void Load(string stateFilepath)
		{
			foreach(var line in File.ReadLines(stateFilepath))
			{
				if(string.IsNullOrWhiteSpace(line))
					continue;
				var flagData = JsonHelper.TryParseJson<FlagData>(line);
				if(flagData?.contractAddr == null)
					continue;

				InsertInternal(flagData);
			}
		}

		private void InsertInternal(FlagData flagData)
		{
			dict.AddOrUpdate(flagData.contractAddr, new HashSet<FlagData>(new FlagData.Comparer()) {flagData}, (key, set) =>
			{
				lock(set)
				{
					set.Remove(flagData);
					set.Add(flagData);
				}
				return set;
			});
		}

		ConcurrentDictionary<string, HashSet<FlagData>> dict = new ConcurrentDictionary<string, HashSet<FlagData>>();
		private StreamWriter stateWriter;
	}
}