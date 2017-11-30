FROM mono:5.4.1.6
WORKDIR /home/TreasureMap/
CMD nuget restore && \
	msbuild /p:Configuration=Release \
			/p:DeployType=ReadyToUpload \
			/t:rebuild TreasureMap.sln && \
	mkdir -p bin/Release/dump && \
	mono bin/Release/TreasureMap.exe
