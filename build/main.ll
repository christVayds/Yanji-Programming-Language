; ModuleID = "module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"

declare i32 @"printf"(i8* %".1", ...)

@"num" = internal global i32 30
@"pnum" = internal global i32* @"num"
@"c" = internal global i8 99
define i32 @"main"()
{
entry:
  %"greet" = getelementptr inbounds [12 x i8], [12 x i8]* @"str_ptr_0", i32 0, i32 0
  %"greet.1" = alloca i8*
  store i8* %"greet", i8** %"greet.1"
  %"greet.2" = load i8*, i8** %"greet.1"
  %"writename_2" = getelementptr inbounds [3 x i8], [3 x i8]* @"str_ptr_1", i32 0, i32 0
  %".3" = call i32 (i8*, ...) @"printf"(i8* %"writename_2", i8* %"greet.2")
  ret i32 0
}

@"str_ptr_0" = internal constant [12 x i8] c"hello world\00"
@"str_ptr_1" = internal constant [3 x i8] c"%s\00"