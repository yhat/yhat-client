Added to docs
- [X] Yhat.predict(args=['self', 'model', 'data', 'model_owner', 'raw_input'])
- [X] Yhat.deploy(args=['self', 'name', 'model', 'session', 'sure', 'packages', 'patch', 'dry_run', 'verbose'])
- [X] YhatModel.execute()
- [X] YhatModel.@preprocess(in_type,out_type)

Hidden from docs until we re-add w/ SSL/TLS and test
- [ ] Yhat.yield_results(args=['self'], varargs=None, keywords=None, defaults=None)
- [ ] Yhat.predict_ws(args=['self', 'data'], varargs=None, keywords=None, defaults=None)
- [ ] Yhat.connect_to_socket(args=['self', 'model', 'model_owner'], varargs=None, keywords=None, defaults=(None,))
- [ ] Yhat.handshake(args=['self', 'model_name', 'model_owner'], varargs=None, keywords=None, defaults=(None,))

To Delete from CLI
- [ ] Yhat.deploy_to_file(args=['self', 'name', 'model', 'session', 'compress', 'packages', 'patch'])
- [ ] Yhat.deploy_with_scp(args=['self', 'name', 'model', 'sessions', 'compress', 'packages', 'pem_path'])
- [ ] YhatModel.execution_plan(args=['self', 'data'])
- [ ] YhatModel.run(args=['self', 'testcase'], varargs=None, keywords=None, defaults=(None,))

Private methods - keep these, but add _{{func_name}} so they are private functions
- [ ] Yhat.get(args=['self', 'endpoint', 'params'], varargs=None, keywords=None, defaults=None)
- [ ] Yhat.post(args=['self', 'endpoint', 'params', 'data', 'pb'], varargs=None, keywords=None, defaults=(False,))
- [ ] Yhat.post_file(args=['self', 'endpoint', 'params', 'data', 'pb'], varargs=None, keywords=None, defaults=(True,))