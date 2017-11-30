mk %1\deploy\service
mk %1\deploy\service\dump


copy %2\*.exe %1\deploy\service
copy %2\*.dll %1\deploy\service
copy %2\*.pdb %1\deploy\service
copy %2\*.config %1\deploy\service
copy %2\settings %1\deploy\service

del %1\deploy\service\JetBrains.Annotations.dll
