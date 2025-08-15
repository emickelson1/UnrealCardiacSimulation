// // Fill out your copyright notice in the Description page of Project Settings.

// #pragma once

// #include "CoreMinimal.h"
// #include "EditorUtilityWidget.h"

// #include "PhysicsEngine/PhysicsAsset.h"

// #include "GeneratePhysicsBodies.generated.h"

// /**
//  * Generate physics bodies for the selected physics assets.
//  */
// UCLASS()
// class SIMULATION_API UGeneratePhysicsBodies : public UEditorUtilityWidget
// {
// 	GENERATED_BODY()
	
// public:
// 	UFUNCTION(BlueprintCallable, Category = "Editor Utils")
// 	TArray<UPhysicsAsset*> GetSelectedPhysicsAssets();

// 	UFUNCTION(BlueprintCallable, Category = "Editor Utils")
// 	bool GenerateBodies();
// };
