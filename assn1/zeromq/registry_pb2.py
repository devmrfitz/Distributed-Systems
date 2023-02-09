# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: registry.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0eregistry.proto\x12\x08tutorial\"\x98\x01\n\x0e\x41rticleRequest\x12\x32\n\x04type\x18\x01 \x01(\x0e\x32$.tutorial.ArticleRequest.ArticleType\x12\x0e\n\x06\x61uthor\x18\x02 \x01(\t\x12\x0c\n\x04time\x18\x03 \x01(\t\"4\n\x0b\x41rticleType\x12\n\n\x06SPORTS\x10\x00\x12\x0b\n\x07\x46\x41SHION\x10\x01\x12\x0c\n\x08POLITICS\x10\x02\"E\n\x07\x41rticle\x12)\n\x07\x61rticle\x18\x01 \x01(\x0b\x32\x18.tutorial.ArticleRequest\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\t\"\xef\x05\n\x07Request\x12#\n\x04type\x18\x01 \x01(\x0e\x32\x15.tutorial.RequestType\x12<\n\x0fregisterRequest\x18\x02 \x01(\x0b\x32!.tutorial.Request.RegisterRequestH\x00\x12\x46\n\x14getServerListRequest\x18\x03 \x01(\x0b\x32&.tutorial.Request.GetServerListRequestH\x00\x12@\n\x11joinServerRequest\x18\x04 \x01(\x0b\x32#.tutorial.Request.JoinServerRequestH\x00\x12\x42\n\x12leaveServerRequest\x18\x05 \x01(\x0b\x32$.tutorial.Request.LeaveServerRequestH\x00\x12\x42\n\x12getArticlesRequest\x18\x06 \x01(\x0b\x32$.tutorial.Request.GetArticlesRequestH\x00\x12H\n\x15publishArticleRequest\x18\x07 \x01(\x0b\x32\'.tutorial.Request.PublishArticleRequestH\x00\x1a\x30\n\x0fRegisterRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07\x61\x64\x64ress\x18\x02 \x01(\t\x1a\x16\n\x14GetServerListRequest\x1a!\n\x11JoinServerRequest\x12\x0c\n\x04uuid\x18\x01 \x01(\t\x1a\"\n\x12LeaveServerRequest\x12\x0c\n\x04uuid\x18\x01 \x01(\t\x1a\x46\n\x12GetArticlesRequest\x12\x30\n\x0e\x61rticleRequest\x18\x01 \x01(\x0b\x32\x18.tutorial.ArticleRequest\x1a;\n\x15PublishArticleRequest\x12\"\n\x07\x61rticle\x18\x01 \x01(\x0b\x32\x11.tutorial.ArticleB\x0f\n\rrequest_oneof\"\xd0\x03\n\x08Response\x12-\n\x04type\x18\x01 \x01(\x0e\x32\x1f.tutorial.Response.ResponseType\x12\x0f\n\x07success\x18\x02 \x01(\x08\x12\x45\n\x13getArticlesResponse\x18\x03 \x01(\x0b\x32&.tutorial.Response.GetArticlesResponseH\x00\x12\x43\n\x12serverListResponse\x18\x04 \x01(\x0b\x32%.tutorial.Response.ServerListResponseH\x00\x1a:\n\x13GetArticlesResponse\x12#\n\x08\x61rticles\x18\x01 \x03(\x0b\x32\x11.tutorial.Article\x1a|\n\x12ServerListResponse\x12=\n\x07servers\x18\x01 \x03(\x0b\x32,.tutorial.Response.ServerListResponse.Server\x1a\'\n\x06Server\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07\x61\x64\x64ress\x18\x02 \x01(\t\",\n\x0cResponseType\x12\x0b\n\x07\x41RTICLE\x10\x01\x12\x0f\n\x0bSERVER_LIST\x10\x02\x42\x10\n\x0eresponse_oneof*z\n\x0bRequestType\x12\x0c\n\x08REGISTER\x10\x00\x12\x13\n\x0fGET_SERVER_LIST\x10\x01\x12\x0f\n\x0bJOIN_SERVER\x10\x02\x12\x10\n\x0cLEAVE_SERVER\x10\x03\x12\x10\n\x0cGET_ARTICLES\x10\x04\x12\x13\n\x0fPUBLISH_ARTICLE\x10\x05')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'registry_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _REQUESTTYPE._serialized_start=1475
  _REQUESTTYPE._serialized_end=1597
  _ARTICLEREQUEST._serialized_start=29
  _ARTICLEREQUEST._serialized_end=181
  _ARTICLEREQUEST_ARTICLETYPE._serialized_start=129
  _ARTICLEREQUEST_ARTICLETYPE._serialized_end=181
  _ARTICLE._serialized_start=183
  _ARTICLE._serialized_end=252
  _REQUEST._serialized_start=255
  _REQUEST._serialized_end=1006
  _REQUEST_REGISTERREQUEST._serialized_start=713
  _REQUEST_REGISTERREQUEST._serialized_end=761
  _REQUEST_GETSERVERLISTREQUEST._serialized_start=763
  _REQUEST_GETSERVERLISTREQUEST._serialized_end=785
  _REQUEST_JOINSERVERREQUEST._serialized_start=787
  _REQUEST_JOINSERVERREQUEST._serialized_end=820
  _REQUEST_LEAVESERVERREQUEST._serialized_start=822
  _REQUEST_LEAVESERVERREQUEST._serialized_end=856
  _REQUEST_GETARTICLESREQUEST._serialized_start=858
  _REQUEST_GETARTICLESREQUEST._serialized_end=928
  _REQUEST_PUBLISHARTICLEREQUEST._serialized_start=930
  _REQUEST_PUBLISHARTICLEREQUEST._serialized_end=989
  _RESPONSE._serialized_start=1009
  _RESPONSE._serialized_end=1473
  _RESPONSE_GETARTICLESRESPONSE._serialized_start=1225
  _RESPONSE_GETARTICLESRESPONSE._serialized_end=1283
  _RESPONSE_SERVERLISTRESPONSE._serialized_start=1285
  _RESPONSE_SERVERLISTRESPONSE._serialized_end=1409
  _RESPONSE_SERVERLISTRESPONSE_SERVER._serialized_start=1370
  _RESPONSE_SERVERLISTRESPONSE_SERVER._serialized_end=1409
  _RESPONSE_RESPONSETYPE._serialized_start=1411
  _RESPONSE_RESPONSETYPE._serialized_end=1455
# @@protoc_insertion_point(module_scope)
