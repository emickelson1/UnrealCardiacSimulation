// // Fill out your copyright notice in the Description page of Project Settings.


// #include "GeneratePhysicsBodies.h"

// #include "PhysicsEngine/PhysicsAsset.h"
// #include "PhysicsEngine/IPhysicsAssetEditor.h"
// #include "AssetRegistry/AssetRegistryModule.h"
// #include "Editor.h"
// #include "ContentBrowserModule.h"
// #include "IContentBrowserSingleton.h"


// TArray<UPhysicsAsset*> UGeneratePhysicsBodies::GetSelectedPhysicsAssets(){
//     TArray<UPhysicsAsset*> selectedAssets;
//     TArray<FAssetData> selectedPhysicsAssets;
//     IContentBrowserSingleton& ContentBrowser = FModuleManager::LoadModuleChecked<FContentBrowserModule>("ContentBrowser").Get();
//     ContentBrowser.GetSelectedAssets(selectedAssets);

//     for (const FAssetData& assetData : selectedAssets)
//     {
//         if (UPhysicsAsset* PhysAsset = Cast<UPhysicsAsset>(assetData.GetAsset()))
//         {
//             selectedPhysicsAssets.Add(PhysAsset);
//         }
//     }
//     return selectedPhysicsAssets;
// }

// bool UGeneratePhysicsBodies::GenerateBodies()
// {
//     TArray<UPhysicsAsset*> selectedAssets = GetSelectedPhysicsAssets();
//     if (selectedAssets.Num() == 0)
//     {
//         return false;
//     }

//     #if WITH_EDITOR
//         for (UPhysicsAsset* physAsset : selectedAssets)
//         {
//             // Generate bodies for each selected physics asset
//             if (!physAsset || !physAsset->GetPreviewMesh())
//             {
//                 UE_LOG(LogTemp, Warning, TEXT("PhysicsAsset has no preview mesh."));
//                 return;
//             }

//             USkeletalMesh* skelMesh = physAsset->GetPreviewMesh();
//             if (!skelMesh)
//                 return;

//             // Remove existing bodies and constraints
//             physAsset->ClearAllBodies();
//             physAsset->ClearConstraints();

//             // Create from skeletal mesh
//             FPhysAssetCreateParams newParams;
//             newParams.VertWeight = 0.5f;      // weight threshold
//             newParams.MinBoneSize = 0.0f;
//             newParams.BodyForAll = true;
//             newParams.GeomType = EPhysAssetFitGeomType::EFG_MultiConvexHull
//             newParams.HullCount = 8
//             newParams.MaxHullVerts = 32

//             FPhysicsAssetUtils::CreateFromSkeletalMesh(physAsset, skelMesh, NewParams);

//             physAsset->MarkPackageDirty();
//         }
//     #endif
//     return true;
// }